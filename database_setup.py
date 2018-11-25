import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class BookCategory(Base):
    __tablename__ = 'bookCategory'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Book(Base):
    __tablename__ = 'book'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    language = Column(String(250))
    bookCategory_id = Column(Integer, ForeignKey('bookCategory.id'))
    bookCategory = relationship(BookCategory)


engine = create_engine('sqlite:///bookstore.db')


Base.metadata.create_all(engine)