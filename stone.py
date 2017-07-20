# 导入:
import sys

import sqlite3
from sqlalchemy import Column, String, create_engine, Integer,DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# 创建对象的基类:
Base = declarative_base()

# 定义User对象:
class booklist(Base):
    # 表的名字:
    __tablename__ = 'booklist'

    # 表的结构:
    id = Column(Integer(),primary_key=True)
    bookname = Column(String(20))
    bookchapter=Column(String(100))
    chapterurl=Column(String(100))
    chaptercontent=Column(String(8000))
    chapterdate=Column(DateTime())
    #
    # def __str__(self):
    #     return self.bookchapter

# 初始化数据库连接:
# print(sys.path[0])
cx=sqlite3.connect(sys.path[0]+"/study.sqlite3")
engine = create_engine("sqlite:///"+sys.path[0]+"/study.sqlite3", echo=True)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
session = DBSession()

def save(bookname,bookchapter,chapterurl,chaptercontent,chapterdate= datetime.now()):
    session.add(booklist(bookname=bookname,bookchapter=bookchapter,chapterurl=chapterurl,chaptercontent=chaptercontent,chapterdate=chapterdate))
    session.commit()
    session.close()

def query(str):
    return session.query(booklist).filter(booklist.bookchapter==str).one()


# for list in session.query(booklist).all():
#     print(list.bookchapter)
# print('______________')
# print(session.query(booklist).filter(booklist.bookchapter=='第1214章 聊够了没').one().bookchapter)
# def query():
#     return session.query(booklist).one().bookchapter
# NoResultFound