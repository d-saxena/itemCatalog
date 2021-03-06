from flask import Flask, render_template, request, redirect
from flask import url_for, jsonify, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, BookCategory, Book, User
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Book Store Catalog Application"

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
    return render_template('bookStoreLogin.html', STATE=state)


# Authentication using Google OAuth
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # If user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# To create new user
def createUser(login_session):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# To get user Information
def getUserInfo(user_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


# To get users information
def getUserID(email):
    try:
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Disconnects the already connected user
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps
                                 ('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        flash("You have successfully been logged out.")
        return redirect(url_for('showBookCategories'))
    else:
        response = make_response(json.dumps
                                 ('Failed to revoke token for user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all users JSON file
@app.route('/users/JSON')
def showUsersJSON():
    user = session.query(User).all()
    return jsonify(user=[u.serialize for u in user])


# Returns the JSON of the books for a category
@app.route('/bookCategory/<int:bookCategory_id>/books/JSON')
def bookCategoryJSON(bookCategory_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    bookCategory = session.query(
        BookCategory).filter_by(id=bookCategory_id).one()
    books = session.query(Book).filter_by(
        bookCategory_id=bookCategory_id).all()
    return jsonify(Books=[i.serialize for i in books])


# Returns the JSON of the particular book
@app.route('/bookCategory/<int:bookCategory_id>/books/<int:book_id>/JSON')
def bookJSON(bookCategory_id, book_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    book = session.query(Book).filter_by(id=book_id).one()
    return jsonify(Book=book.serialize)


# Returns the JSON of the all the book categories
@app.route('/bookCategory/JSON')
def bookCategoriesJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    bookCategories = session.query(BookCategory).all()
    return jsonify(BookCategories=[b.serialize for b in bookCategories])


# Shows all the available book category
@app.route('/')
@app.route('/bookCategory/')
def showBookCategories():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    bookCategories = session.query(
        BookCategory).order_by(asc(BookCategory.name))
    return render_template('bookCategories.html',
                           bookCategories=bookCategories)


# Create a new book category
@app.route('/bookCategory/new/', methods=['GET', 'POST'])
def newBookCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        newBookCategory = BookCategory(name=request.form['name'],
                                       user_id=login_session['user_id'])
        session.add(newBookCategory)
        flash('New Book Category %s Successfully Created' %
              newBookCategory.name)
        session.commit()
        return redirect(url_for('showBookCategories'))
    else:
        return render_template('newBookCategory.html')


# Edit a Book Category
@app.route('/bookCategory/<int:bookCategory_id>/edit/',
           methods=['GET', 'POST'])
def editBookCategory(bookCategory_id):
    if 'username' not in login_session:
        return redirect('/login')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedBookCategory = session.query(
        BookCategory).filter_by(id=bookCategory_id).one()
    if editedBookCategory.user_id != login_session['user_id']:
        flash("You are not authorised to edit this Book Category. Please \
        create your own Category in order to edit")
        return redirect(url_for('showBookCategories',
                        bookCategory_id=bookCategory_id))
    if request.method == 'POST':
        if request.form['name']:
            editedBookCategory.name = request.form['name']
            session.add(editedBookCategory)
            flash('Book Category Successfully Edited %s' %
                  editedBookCategory.name)
            session.commit()
            return redirect(url_for('showBookCategories'))
    else:
        return render_template('editBookCategory.html',
                               bookCategory=editedBookCategory)


# Delete a Book Category
@app.route('/bookCategory/<int:bookCategory_id>/delete/',
           methods=['GET', 'POST'])
def deleteBookCategory(bookCategory_id):
    if 'username' not in login_session:
        return redirect('/login')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    bookCategoryToDelete = session.query(
        BookCategory).filter_by(id=bookCategory_id).one()
    books = session.query(Book).filter_by(
        bookCategory_id=bookCategory_id).all()
    if bookCategoryToDelete.user_id != login_session['user_id']:
        flash("You are not authorised to delete this Book Category.Please \
        create your own Category in order to delete")
        return redirect(url_for('showBookCategories',
                        bookCategory_id=bookCategory_id))
    if request.method == 'POST':
        for b in books:
            session.delete(b)
            session.commit()
        session.delete(bookCategoryToDelete)
        flash('%s Successfully Deleted' % bookCategoryToDelete.name)
        session.commit()
        return redirect(url_for('showBookCategories',
                        bookCategory_id=bookCategory_id))
    else:
        return render_template('deleteBookCategory.html',
                               bookCategory=bookCategoryToDelete)


# Show books under a book category
@app.route('/bookCategory/<int:bookCategory_id>/')
@app.route('/bookCategory/<int:bookCategory_id>/books/')
def showBooks(bookCategory_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    bookCategory = session.query(
        BookCategory).filter_by(id=bookCategory_id).one()
    books = session.query(Book).filter_by(
        bookCategory_id=bookCategory_id).all()
    return render_template('books.html', books=books,
                           bookCategory=bookCategory)


# Create a new book under a book category
@app.route('/bookCategory/<int:bookCategory_id>/books/new/',
           methods=['GET', 'POST'])
def newBook(bookCategory_id):
    if 'username' not in login_session:
        return redirect('/login')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    bookCategory = session.query(
        BookCategory).filter_by(id=bookCategory_id).one()
    if login_session['user_id'] != bookCategory.user_id:
        flash("You are not authorized. Please create your own Category in \
         order to add book.")
        return redirect(url_for('showBookCategories',
                                bookCategory_id=bookCategory_id))
    if request.method == 'POST':
        newBook = Book(name=request.form['name'], description=request.form[
                       'description'], price=request.form['price'],
                       language=request.form['language'],
                       bookCategory_id=bookCategory_id,
                       user_id=bookCategory.user_id)
        session.add(newBook)
        session.commit()
        flash('New Book %s Successfully Created' % (newBook.name))
        return redirect(url_for('showBookCategories',
                                bookCategory_id=bookCategory_id))
    else:
        return render_template('newBook.html', bookCategory_id=bookCategory_id)


# Edit a book under a book category
@app.route('/bookCategory/<int:bookCategory_id>/books/<int:book_id>/edit',
           methods=['GET', 'POST'])
def editBook(bookCategory_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedBook = session.query(Book).filter_by(id=book_id).one()
    bookCategory = session.query(
        BookCategory).filter_by(id=bookCategory_id).one()
    if login_session['user_id'] != bookCategory.user_id:
        flash("You are not authorized \
        to edit books of this category. Please create your own category\
         in order to edit books.")
        return redirect(url_for('showBookCategories',
                                bookCategory_id=bookCategory_id))
    if request.method == 'POST':
        if request.form['name']:
            editedBook.name = request.form['name']
        if request.form['description']:
            editedBook.description = request.form['description']
        if request.form['price']:
            editedBook.price = request.form['price']
        if request.form['language']:
            editedBook.language = request.form['language']
        session.add(editedBook)
        session.commit()
        flash('Book Successfully Edited')
        return redirect(url_for('showBooks', bookCategory_id=bookCategory_id))
    else:
        return render_template('editBook.html',
                               bookCategory_id=bookCategory_id,
                               book_id=book_id, book=editedBook)


# Delete a book under a book category
@app.route('/bookCategory/<int:bookCategory_id>/books/<int:book_id>/delete',
           methods=['GET', 'POST'])
def deleteBook(bookCategory_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    bookCategory = session.query(
        BookCategory).filter_by(id=bookCategory_id).one()
    bookToDelete = session.query(Book).filter_by(id=book_id).one()
    if login_session['user_id'] != bookCategory.user_id:
        flash("You are not authorized \
        to delete book of this category. Please create your own category \
        in order to delete books.")
        return redirect(url_for('showBookCategories',
                                bookCategory_id=bookCategory_id))
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        flash('Book Successfully Deleted')
        return redirect(url_for('showBooks', bookCategory_id=bookCategory_id))
    else:
        return render_template('deleteBook.html', book=bookToDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
