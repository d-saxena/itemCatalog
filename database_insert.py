from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BookCategory, Book

engine = create_engine('sqlite:///bookstore.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

bookCategory = BookCategory(name = "Psychology")
session.add(bookCategory)

book1 = Book(name = "Train your brain", description = "Description 1", language = "English", price = "35", bookCategory = bookCategory)
book2 = Book(name = "Attitude is Everything", description = "Description 2", language = "English", price = "22", bookCategory = bookCategory)
book3 = Book(name = "Believe in Yourself", description = "Description 3", language = "English", price = "10", bookCategory = bookCategory)
book4 = Book(name = "Khud pe Bharosa", description = "Description 4", language = "Hindi", price = "15", bookCategory = bookCategory)
book5 = Book(name = "Kamiyab Insaan", description = "Description 5", language = "Hindi", price = "25", bookCategory = bookCategory)
book6 = Book(name = "Takdeer ka ilm", description = "Description 6", language = "Urdu", price = "25", bookCategory = bookCategory)
session.add(book1)
session.add(book2)
session.add(book3)
session.add(book4)
session.add(book5)
session.add(book6)

bookCategory = BookCategory(name = "Comedy")
session.add(bookCategory)

book1 = Book(name = "Fun with brain", description = "Description 1", language = "English", price = "35", bookCategory = bookCategory)
book2 = Book(name = "Fun is Everything", description = "Description 2", language = "English", price = "22", bookCategory = bookCategory)
book3 = Book(name = "Fun in Yourself", description = "Description 3", language = "English", price = "10", bookCategory = bookCategory)
book4 = Book(name = "Majak ka sahara", description = "Description 4", language = "Hindi", price = "15", bookCategory = bookCategory)
book5 = Book(name = "Majakiya Insaan", description = "Description 5", language = "Urdu", price = "25", bookCategory = bookCategory)
session.add(book1)
session.add(book2)
session.add(book3)
session.add(book4)
session.add(book5)
session.add(book6)

session.commit()
