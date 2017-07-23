import sqlite3
import sys
from sqlalchemy import Column, Integer, String, DateTime, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

cx=sqlite3.connect(sys.path[0]+"/book.sqlite3")
engine = create_engine("sqlite:///"+sys.path[0]+"/book.sqlite3", echo=True)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

# 创建对象的基类:
Base = declarative_base()
# 连接数据库
session = DBSession()
# 定义booklist对象:
class BookList(Base):
    # 表的名字:
    __tablename__ = 'BookList'

    # 表的结构:
    id = Column(Integer(),primary_key=True)
    bookname = Column(String(20))
    bookchapter=Column(String(100))
    chapterurl=Column(String(100))
    chaptercontent=Column(String(8000))
    chapterdate=Column(DateTime())
    status=Column(Boolean())
    #
    # def __str__(self):
    #     return self.bookchapter

class BookName(Base):
    # 表的名字:
    __tablename__ = 'NovelName'

    # 表的结构:
    id = Column(Integer(),primary_key=True)
    NovelName = Column(String(20))
    BookDirectoryUrl=Column(String(100))
    #
    # def __str__(self):
    #     return self.bookchapter

# 如果没有创建表，则创建
Base.metadata.create_all(engine)


def stoneobject():
    return session

