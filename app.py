
import os
from re import M, search
from unicodedata import category
import requests
import json
import psycopg2
import itertools 

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify,url_for,abort
from sqlalchemy.exc import IntegrityError

from forms import LoginForm, UserAddForm, PasswordResetForm 
from models import db, connect_db, User,Addproduct, FavoriteProduct
from helpers import get_products_from_api_response

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.jinja_env.filters['zip'] = zip 

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///eCommerce')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False 
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")



API_BASE_URL = "https://fakestoreapi.com"

connect_db(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.create_all()
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/")
    #######################################################


@app.route('/')
def show_products_form():
    stores = most_popular_products()

    return render_template("home.html", stores=stores)



@app.route('/index',methods=['POST', 'GET'])
def product_by_name():

    res = requests.get('https://fakestoreapi.com/products',
                       )

    data = res.json()

    if data.get('items') == None:
        flash("No item name found", "danger")
        return redirect('/')
    else:

        stores = get_products_from_api_response(data)

    return render_template('stores/index.html', stores=stores)




##############################################################################
# The navbar route Links


def most_popular_products():
    res = requests.get('https://fakestoreapi.com/products',
                       )

    data = res.json()
    return get_products_from_api_response(data)

##### This gives you a list of categories###
@app.route('/category')
def item_by_category():

    
    selected_category = request.args.get('selected_category')
    stores = []
    
    if  selected_category:
        res = requests.get('https://fakestoreapi.com/products/category/'+ selected_category
        )  
        
    
        data = res.json()
        stores = get_products_from_api_response(data)

    return render_template('stores/category.html', stores=stores)


#############################################################################
# Get all the details of the product: Needs fixing

@app.route('/product_detail')
def details_by_id():
    

    product_id =request.args.get('product_id')
    
    
    res = requests.get('https://fakestoreapi.com/products/'+ product_id)  

    data = res.json()
    
    

    stores = []

    
    for item in data:
       
         store = {
            'id': item ['id'],
            'title': item['title'],
            'image': item['image'],
            'description': item['description'],
            'price':item['price'] 
        }

         stores.append(store)

    return render_template('stores/product_detail.html', stores=stores)

##############################################################################
# User Homepage- Needs Fixing


@app.route('/users/favorite')
def user_favorite():

    user_id = g.user.id
    user = User.query.get_or_404(user_id)

    if user:

        all_items = FavoriteProduct.query.filter_by(
            user_id=user_id).order_by(FavoriteProduct.id.desc()).all()

        shops = []
        for item in all_items:
            shop = {'name': item.item_name,
                        'id': item.item_id, 'thumb': item.item_thum}

            shops.append(shop)

        return render_template("users/favorite.html", user=user, shops=shops, show_delete=True)
    else:
        return render_template("users/favorite.html")


@app.route('/users/favorite/<int:item_id>', methods=["GET", "POST"])
def add_favorite(item_id):
    """Add Item id to user favorite."""

    user_id = g.user.id
    user = User.query.get_or_404(user_id)

    item_object = FavoriteProduct.query.filter_by(
        item_id=str(item_id),
        user_id=str(user_id)
    ).all()

    if not item_object:
        res = requests.get(f"{API_BASE_URL}/product",
                          )

        data = res.json()
        item = data['items'][0]
        item_id = item['id']
        item_name = item['title']
        item_thum = item['image']

        new_item = FavoriteProduct(item_id=item_id,
                                  item_name=item_name, item_thum=item_thum, user_id=user_id)

        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for('user_favorite.html'))

    else:
        flash("Item already in favorites!", "danger")
        return redirect(url_for('show_product_for')) 

# -------------------- Remove the favorite product  --------------------------->


@app.route('/users/delete/<int:item_id>', methods=["GET", "POST"])
def delete_item(item_id):
    """Have currently-logged-in-user delete product."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_favorite_product = FavoriteProduct.query.filter_by(
        item_id=str(g.user.id)
    ).first()

    db.session.delete(user_favorite_product)
    db.session.commit()

    return redirect("/users/favorite.html")



##############################################################################


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404/404.html'), 404


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@ app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req