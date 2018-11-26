from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BookCategory, Book
from flask import session as login_session
import random, string

app = Flask(__name__)

engine = create_engine('sqlite:///bookstore.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return "The current session state is %s" % login_session['state']

@app.route('/bookCategory/<int:bookCategory_id>/books/JSON')
def bookCategoryJSON(bookCategory_id):
    bookCategory = session.query(BookCategory).filter_by(id=bookCategory_id).one()
    books = session.query(Book).filter_by(
        bookCategory_id=bookCategory_id).all()
    return jsonify(Books=[i.serialize for i in books])

@app.route('/bookCategory/<int:bookCategory_id>/books/<int:book_id>/JSON')
def bookJSON(bookCategory_id, book_id):
    book = session.query(Book).filter_by(id=book_id).one()
    return jsonify(Book=book.serialize)   

@app.route('/')
@app.route('/bookCategory/<int:bookCategory_id>/')
def listofbooks(bookCategory_id):
    bookCategory = session.query(BookCategory).filter_by(id = bookCategory_id).one()
    books = session.query(Book).filter_by(bookCategory_id=bookCategory_id)
    output = ''
    for i in books:
        output += i.name
        output += '</br>'
        output += i.price
        output += '</br>'
        output += i.description
        output += '</br>'
        output += '</br>'       
    return output

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)