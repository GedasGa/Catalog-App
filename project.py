from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

import os
import sys
import datetime

from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Flask Login Decorator
def login_required(f):
    @wraps(f)
    def decorated_fuction(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_fuction


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


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
        response = make_response(json.dumps('This user is already connected.'),
                                 200)
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

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    output += ' -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        del login_session['provider']
        flash("You have Successfully logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in.")
        return redirect(url_for('showCategories'))


# JSON endpoint
@app.route('/catalog.json')
def getCatalog():
    output_json = []
    categories = session.query(Category).all()
    for category in categories:
        items = session.query(CatalogItem).filter_by(category_id=category.id)
        category_output = {}
        category_output["id"] = category.id
        category_output["name"] = category.name
        category_output["Items"] = [i.serialize for i in items]
        output_json.append(category_output)
    return jsonify(Categories=output_json)


# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    lastest_items = session.query(CatalogItem).order_by(
        desc(CatalogItem.date)).limit(5)
    if 'username' not in login_session:
        return render_template('catalogpublic.html', categories=categories,
                               items=lastest_items)
    else:
        return render_template('catalog.html', categories=categories,
                               items=lastest_items)


# Show a category
@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(CatalogItem).filter_by(
        category_id=category.id).all()
    creator = getUserInfo(category.user_id)
    count = session.query(CatalogItem).filter_by(category=category).count()
    if 'username' not in login_session:
        return render_template('catalogitempublic.html', items=items,
                               category=category, categories=categories,
                               creator=creator, count=count)
    else:
        return render_template('catalogitem.html', items=items,
                               category=category, categories=categories,
                               count=count)


# Show a category item
@app.route('/catalog/<string:category_name>/<string:catalog_item_title>/')
def showItem(category_name, catalog_item_title):
    categories = session.query(Category).order_by(asc(Category.name))
    item = session.query(CatalogItem).filter_by(title=catalog_item_title).one()
    creator = getUserInfo(item.user_id)
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('itemdetailspublic.html', item=item,
                               category=category_name, categories=categories,
                               creator=creator)
    else:
        return render_template('itemdetails.html', item=item,
                               category=category_name, categories=categories,
                               creator=creator)


# Create a new catalog item
@app.route('/catalog/items/new/', methods=['GET', 'POST'])
@login_required
def newCatalogItem():
    categories = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).one()
        creator = session.query(User).filter_by(
            name=login_session['username']).one()
        newItem = CatalogItem(title=request.form['title'],
                              description=request.form['description'],
                              category_id=category.id,
                              category=category, user_id=creator.id,
                              user=creator, date=datetime.datetime.now())
        session.add(newItem)
        session.commit()
        flash('New Catalog %s Item Successfully Created' % (newItem.title))
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcatalogitem.html', categories=categories)


# Edit a catalog item
@app.route('/catalog/<string:catalog_item_title>/edit',
           methods=['GET', 'POST'])
@login_required
def editCatalogItem(catalog_item_title):
    categories = session.query(Category).order_by(asc(Category.name))
    editedItem = session.query(CatalogItem).filter_by(
        title=catalog_item_title).one()
    category = session.query(Category).filter_by(
        id=editedItem.category_id).one()
    creator = getUserInfo(editedItem.user_id)
    if login_session['user_id'] != creator.id:
        flash('You can\'t edit this Item, because you didn\'t create it')
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            category_name = request.form['category']
            category = session.query(Category).filter_by(
                name=category_name).one()
            editedItem.category_id = category.id
        session.add(editedItem)
        session.commit()
        flash('Catalog Item Successfully Edited')
        return redirect(url_for('showCategories'))
    else:
        return render_template('editcatalogitem.html', categories=categories,
                               item=editedItem)


# Delete a catalog item
@app.route('/catalog/<string:catalog_item_title>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteCatalogItem(catalog_item_title):
    itemToDelete = session.query(CatalogItem).filter_by(
        title=catalog_item_title).one()
    category = session.query(Category).filter_by(
        id=itemToDelete.category_id).one()
    creator = getUserInfo(itemToDelete.user_id)
    if login_session['user_id'] != creator.id:
        flash('You can\'t delete this Item, because you didn\'t create it')
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Catalog Item Successfully Deleted')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deletecatalogitem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
