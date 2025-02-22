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

app = Flask(__name__)
app.secret_key = "REPLACE_ME_WITH_RANDOM_CHARACTERS"

db_name = "A3.db"
sqlite_uri = f"sqlite:///{os.path.abspath(os.path.curdir)}/{db_name}"
app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from models import User

with app.app_context():
    db.create_all()


@app.before_request
def check_login():

@app.route('/')
def index():
    return 'Results of GET /'

# Show login form
@app.route('/login', methods=['GET'])
def login_form():
    return 'Show login form'

# Process login form submission
@app.route('/login', methods=['POST'])
def login():
    return 'Process login'

# Show registration form
@app.route('/register', methods=['GET'])
def register_form():
    return 'Show registration form'

# Process registration form submission
@app.route('/register', methods=['POST'])
def register():
    return 'Process registration'

# Display items summary page
@app.route('/items', methods=['GET'])
def items_summary():
    return 'Display items summary'

# Show item details page
@app.route('/item/<int:item_id>', methods=['GET'])
def item_detail(item_id):
    return f'Show item details for item {item_id}'

# Add item to the cart and redirect to cart
@app.route('/cart/add/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    return f'Add item {item_id} to cart'

# Show shopping cart
@app.route('/cart', methods=['GET'])
def cart():
    return 'Show shopping cart'

# Remove an item from the cart
@app.route('/cart/delete/<int:item_id>', methods=['POST'])
def delete_from_cart(item_id):
    return f'Remove item {item_id} from cart'

# Show checkout page
@app.route('/checkout', methods=['GET'])
def checkout():
    return 'Show checkout page'

# Process order and confirm purchase
@app.route('/checkout', methods=['POST'])
def process_checkout():
    return 'Process checkout'

# Secret route displaying all orders
@app.route('/orders/', methods=['GET'])
def view_orders():
    return 'Show all orders'

# Log out the user and clear session
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return 'Log out user'


