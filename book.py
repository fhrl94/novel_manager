import smtplib
from datetime import datetime
import time
import re
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import  requests
from bs4 import BeautifulSoup as bs
from requests import ConnectTimeout
# from requests.exceptions import ConnectTimeout
from sqlalchemy.orm.exc import NoResultFound

from novel_manager.stone import stoneobject, BookName, BookList

# 全局数据库链接
global stone
stone=stoneobject()
# 全局list TAG标签
mapping = []
file = open('mapping.txt', 'rb')
for f in file.readlines():
    # print(f.decode('utf-8').replace('\r\n', '', -1))
    mapping.append(f.decode('utf-8').replace('\r\n', '', -1))
# print(mapping)
#

global from_addr,password,to_addr
from_addr=input("请输入发件人邮箱")
password=input("请输入发件人邮箱密码")
to_addr=input("请输入收件人邮箱")


# 打开网页,基于charset，如果设置为设置值，默认为utf-8,返回为解码后的源码
def OpenUrl(url,timeout=10):
    r=requests.get(url=url,timeout=timeout)
    charset = re.compile(r'charset=["]?(.*?)"')
    encoding = re.findall(charset, r.text)
    # print(type(encoding))
    r.encoding='utf-8'
    if encoding :
        r.encoding = encoding[0]
    # print(r.text)
    return r.text

# 使用bs解析str,返回结构化文档
def ParsingString(string):
    return bs(string,'html.parser')

# 获取小说名称
def __GetBookName():

    stone=stoneobject()
    f=open('book.txt','ab+')
    f.seek(0)
    if len(f.read())==0:
        str=input("请输入小说名称")
        f.write(str.encode())
    f.flush()
    f.seek(0)
    return f.readlines()


# 根据小说名称获取目录URL地址，存到bookname中
def GetBookDirectoryUrl_Save():
    str=__GetBookName()
    # stone = stoneobject()
    for s in str:
        # print(s.decode())
        book_name=s.decode().replace('\n', '', -1).replace('\r','',-1)
        url=OpenUrl('http://www.sodu.cc/result.html?searchstr=' + book_name)
        soup=ParsingString(url)
        # print(soup.find_all(attrs='main-html'))
        hrefs=soup.find_all(attrs='main-html')
        for href in hrefs:
            # print(href.a.get('href'))
            if href.a.get('href') !=None:
                BookDirectoryUrl=href.a.get('href')
        try:
            stone.query(BookName).filter(BookName.NovelName == book_name).one()
        except NoResultFound:
            stone.add(BookName(NovelName=book_name, BookDirectoryUrl=BookDirectoryUrl))
            stone.commit()
    # stone.close()

# 打开目录连接跳转到真实链接,并测试是否能打开，返回第一能打开的链接
def OpenBookDirectoryUrl_Test_return(BookDirectoryUrl):
    www=re.compile(r"(?:http|ftp)s?://.*?\.html")
    html=OpenUrl(url=BookDirectoryUrl)
    # print(html)
    soup=ParsingString(html)
    hrefs=soup.find_all(attrs='main-html')
    for i,href in enumerate(hrefs):
        # print(href.a.get('href'))
        url=href.a.get('href')
        bookchapter = href.a.string
        # print('_____')
        # print(bookchapter)
        # print('____')
        # print(url)
        html=OpenUrl(url=url)
        string=re.findall(www,html)
        # print(string)
        try:
            # print(OpenUrl(url=string[0],encoding='gbk'))
            OpenUrl(url=string[0])
            # print(url)
            return bookchapter,string[0]
        except ConnectTimeout:
            print('跳过第%s条' %(i+1))
        if i+1>=10:
            print('网络故障')
            return None

# 获取排名第一的（如果能打开,需要设置超时）网站，获取最新章节URL
def GetChapterUrl_OK():
    # stone = stoneobject()
    # print('-------')
    # print(stone.query(bookname).values(bookname.bookdirectoryurl))
    NovelBooks=stone.query(BookName).order_by(BookName.id).values(BookName.NovelName, BookName.BookDirectoryUrl)
    Novels = []
    Novel_Names=[]
    for Novel_Name,BookDirectoryUrl in NovelBooks:
        # print(Novel_Name,BookDirectoryUrl)
        # print(OpenBookDirectoryUrl_Test_return(BookDirectoryUrl))
        Novel_Names.append(Novel_Name)
        Novels.append(OpenBookDirectoryUrl_Test_return(BookDirectoryUrl))
    for i,Novel in enumerate(Novels):
        try:
            stone.query(BookList).filter(BookList.bookchapter==Novel[0]).one()
        except NoResultFound:
            stone.add(BookList(bookname=Novel_Names[i],bookchapter=Novel[0],chapterurl=Novel[1],chaptercontent=None,chapterdate=datetime.now(),status=True))
            stone.commit()
    # return

# 根据自定义Mapping，选择文本所在标签的类名（class），将文本更新到数据表BookList中chaptercontent
def SelectClass_SaveContent():
    lists = stone.query(BookList).filter(BookList.status == True).all()
    # name=
    # print(string.readline())
    for list in lists:
        # print(type(list))
        print(list.chapterurl)
        html = OpenUrl(list.chapterurl)
        soup = ParsingString(html)
        for tag in mapping:
            # print(soup.select(tag))
            if soup.select(tag):
                content = ''
                for texts in soup.select(tag):
                    # print( text.stripped_strings)
                    for text in texts.stripped_strings:
                        print(text)
                        content = content + text + '\n'
                stone.query(BookList).filter(BookList.id == list.id).update({BookList.chaptercontent: content})
                stone.commit()
# r=requests.get(url='http://www.168xs.com/du/121796/37676436.html')
# print(r.content)

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send(header,body):
    smtp_server =r'smtp.qq.com'
    # smtp_server = r'smtp.163.com'

    # 正文 需要更改为小说章节内容
    msg = MIMEText(body, 'plain', 'utf-8')
    # 主题，需要更改为当前小说章节名
    msg['Subject'] = Header(header, 'utf-8').encode()
    # 发件人别名
    msg['From'] = _format_addr('小说管理站 <%s>' % from_addr)
    # 收件人别名
    msg['To'] = _format_addr('订阅人 <%s>' % to_addr)


    # server = smtplib.SMTP(smtp_server, 25)
    # server.login(from_addr, password)
    server = smtplib.SMTP(smtp_server)
    server.starttls()
    server.login(from_addr, password)
    # server.set_debuglevel(1)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

def Check_Send():
    lists=stone.query(BookList).filter(BookList.status==True).all()
    for list in lists:
        if list.chaptercontent!=None:
            send(list.bookchapter,list.chaptercontent)
            stone.query(BookList).filter(BookList.id==list.id).update({BookList.status:False})
            stone.commit()
        else:
            send(list.bookchapter+"无法解析", list.chapterurl+"请查看原链接，更新TAG")
    try:
        stone.query(BookList).filter(BookList.status==True,BookList.chaptercontent!=None).one()
        Check_Send()
    except NoResultFound:
        time.sleep(60*10)
# 检查表BookList中status为True的行，chaptercontent不为None则发送文本，否则发送错误，同时更新status
# 发送完成后，检查是否还存在chaptercontent不为None且status为True的行，不存在休息15分钟，存在继续调用

if __name__ == '__main__':
# 获取目录URL
    GetBookDirectoryUrl_Save()
    while True:
        try:
            GetChapterUrl_OK()
            SelectClass_SaveContent()
            Check_Send()
        except ConnectTimeout:
            print("网络超时，1分钟后重试")
            time.sleep(60)
