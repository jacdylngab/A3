from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    jsonify,
    abort,
)
from flask_sqlalchemy import SQLAlchemy
import os
from collections import defaultdict
import re

app = Flask(__name__)
app.secret_key = "REPLACE_ME_WITH_RANDOM_CHARACTERS"

db_name = "A2.db"
sqlite_uri = f"sqlite:///{os.path.abspath(os.path.curdir)}/{db_name}"
app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from models import User, Item, Order

with app.app_context():
    db.create_all()


@app.before_request
def check_login():
    if (
        request.path == url_for("register_form")
        or request.path == url_for("login_form")
        or request.path == url_for("orders")
        or request.path == url_for("create_user")
        or request.path.startswith("/static/")
    ):
        pass

    elif "username" not in session:
        return redirect(url_for("login_form"))


# I learned this from ChatGPT. I was having an issue where whenever I pressed
# the back button, it was using the cached version and not the up-to-date version.
# This function ensures that the browser does not cache responses and always
# fetches fresh data when navigating back or refreshing the page.
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def index():
    return redirect(url_for("show_items"))


@app.route("/register/", methods=["GET"])
def register_form():
    return render_template("register_form.html")


@app.route("/register/", methods=["POST"])
def create_user():
    username = request.form["username"]
    realname = request.form["realname"]
    email = request.form["email"]
    mailingaddress = request.form["mailingaddress"]
    creditcard = request.form["creditcard"]
    password = request.form["password"]

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return render_template("register_form.html", message="user already exists")

    # Ensure the credit card is a number and has valid length.
    # We learned how to do this using regular expressions from ChatGPT
    if not re.fullmatch(r"\d{13,19}", creditcard):
        return render_template(
            "register_form.html",
            message="Invalid credit card number. It must be 13-19 digits long.",
        )

    new_user = User(
        username=username,
        realname=realname,
        email=email,
        mailingaddress=mailingaddress,
        creditcard=creditcard,
        password=password,
    )

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("login_form"))


@app.route("/login/", methods=["GET"])
def login_form():
    return render_template("login_form.html")


@app.route("/login/", methods=["POST"])
def do_login():
    username = request.form["username"]
    password = request.form["password"]
    users = User.query.all()
    login = False
    for user in users:
        if user.username == username and user.password == password:
            session["username"] = username
            login = True
            break

    if login:
        return redirect(url_for("show_items"))

    else:
        return render_template("login_form.html", message="Wrong username/password")


@app.route("/items/", methods=["GET"])
def show_items():
    return render_template("show_items.html", items=Item.query.all())


@app.route("/items/<itemid>/", methods=["GET"])
def show_item_detail(itemid):
    item = Item.query.get(itemid)
    if item:
        return render_template("show_item.html", item=item)
    else:
        return "The item you are looking for is not available"


@app.route("/cart/", methods=["POST"])
def add_item_to_cart():
    cart = session.get("cart", {})

    # Get the item ID and use it to get the item name
    item_id = request.form["item"]

    item = Item.query.filter_by(id=item_id).first()

    # If the item exists, we can go ahead and add it to the cart
    if item:
        item_name = item.name
        item_price = item.price

        if item_name in cart:
            cart[item_name]["quantity"] += 1

        else:
            cart[item_name] = {"quantity": 1, "price": item_price}

    # Save the session
    session["cart"] = cart

    return redirect(url_for("show_cart"))


@app.route("/cart/", methods=["GET"])
def show_cart():
    cart = session.get("cart", {})
    total = 0
    if cart:
        for details in cart.values():
            total += details["price"] * details["quantity"]

        total = round(total, 2)  # Round to two decimal places

        return render_template("show_cart.html", cart=cart, total=total)

    else:
        return render_template("cart_empty.html")


@app.route("/logout/", methods=["GET"])
def logout():
    if "cart" in session:
        del session["cart"]
    del session["username"]
    return render_template("login_form.html", message="You have been logged out!")


@app.route("/user-info/", methods=["GET"])
def show_user_detail():
    username = session["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template("show_user.html", user=user)
    else:
        return f"There is no user named {username}."


@app.route("/cart-delete/", methods=["POST"])
def remove_item_from_cart():
    cart = session.get("cart", {})

    item_name = request.form["item-name"]

    # If the item_name exists
    # Remove the item from the cart based on the item_name.
    # Fist check if the cart is empty or not. Only remove the item if the cart is not empty.
    if item_name and cart:
        del cart[item_name]

    # Save the session
    session["cart"] = cart

    return redirect(url_for("show_cart"))


@app.route("/checkout/", methods=["GET"])
def show_checkout():
    cart = session.get("cart", {})
    user = User.query.filter_by(username=session["username"]).first()
    total_price = 0
    if cart:
        total_price = sum(
            details["price"] * details["quantity"] for details in cart.values()
        )

        return render_template(
            "checkout.html",
            cart=cart,
            total=round(total_price, 2),
            user=user,
        )
    else:
        return render_template("cart_empty.html")


@app.route("/checkout/", methods=["POST"])
def complete_checkout():
    cart = session.get("cart", {})
    user = User.query.filter_by(username=session["username"]).first()

    if cart and user:
        # Store checkout details in the orders table in the DB
        new_order = Order(
            username=user.username,
            realname=user.realname,
            mailingaddress=user.mailingaddress,
            cart=cart,
        )

        db.session.add(new_order)
        db.session.commit()

        return redirect(url_for("order_confirmation"))
    else:
        return render_template("cart_empty.html")


@app.route("/orders-confirmation/", methods=["GET"])
def order_confirmation():
    cart = session.get("cart", {})
    if cart:
        # Delete the cart after checking out.
        session["cart"] = {}

        return render_template("order_confirmation.html")
    else:
        return render_template("cart_empty.html")


@app.route("/orders/", methods=["GET"])
def orders():
    orders = Order.query.all()
    grouped_orders = defaultdict(list)

    for order in orders:
        grouped_orders[order.username].append(order)  # Group the orders by the username
    return render_template("orders.html", grouped_orders=grouped_orders)
