from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

import time
import urllib.request

import re
from bs4 import BeautifulSoup as bs


# 打开网页，默认是sodu搜索页面，参数为空，返回为utf-8的字符型
from sqlalchemy.orm.exc import  NoResultFound

from study.stone import save, query


def openurl(argument='',url=r'http://www.sodu.cc/result.html?searchstr=',code='utf-8'):
    '''

    :param argument:查询参数
    :param url:打开的地址
    :param code:解码方式
    :return:字符串string
    '''
    url=url+urllib.request.quote(argument)
    # html=urllib.request.urlopen(url)
    # 模拟浏览器
    req=urllib.request.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36')
    return urllib.request.urlopen(req).read().decode(code)

def bookselect(soup,select='.main-html'):
    '''

    :param soup: BeautifulSoup 对象
    :return: 搜索页面中list对象 第一个是url，第二个是书名，第三个章节名，第四个是最近更新时间，
              非搜索页面中，第一个是url，第二是章节名称，第三个是网站名称，第四个是更新时间，
    '''
    # 筛选class='.main-html'的所有类型（由于网页只可能是div）
    filelist=soup.select(select)
    # 获取链接、书名、章节名、时间
    book=[]
    for files in filelist:
        # print(files.a.get('href'))
        if (files.a!=None):
            book.append(files.a.get('href'))
        for file in files.stripped_strings:
            if(file=='加入书架'):
                continue
            # print(file)
            book.append(file)
            # print(file.string)
    return book

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send(header,body):
    from_addr = input("发件人邮箱")
    password = input("发件人邮箱密码")
    to_addr =input("收件人邮箱")
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

if __name__=='__main__':
    # print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    # sodu网页查询
    str=input("小说名称")
    while True:
        soup=bs(openurl(str),'html.parser')
        # 获取网页查询第一个进行打开
        chapterdate=bookselect(soup)[3]
        bookname=bookselect(soup)[1]
        bookchapter=bookselect(soup)[2]
        # if timeend>timer :
        #     timer=timeend
            # print(1)
        soup=bs(openurl(url=bookselect(soup)[0]),'html.parser')
        # 将当前页面第一个链接进行打开后，通过正则表达式，获取真是链接
        www=re.compile(r"(?:http|ftp)s?://.*?html")
        # 打开链接，解码方式为GBK(卧槽）
        chapterurl=(re.findall(www, openurl(url=bookselect(soup)[0]))[0])
        soup=bs(openurl(url=chapterurl,code='gbk'),'html.parser')
        # 筛选id=content，将值读取到book
        book=bookselect(soup,select='#content')
        # 重置
        body=''
        for b in book:
            # print(b)
            body= body+b +'\n'
        print(body)
        # send(header=header,body=body)
        print(chapterdate)
        try:
            query(bookchapter)
        except NoResultFound:
            save(bookname=str, bookchapter=bookchapter, chapterurl=chapterurl, chaptercontent=body,)
            # print('更新')
            send(header=str+" 更新 "+bookchapter,body=body)
        time.sleep(15*60)