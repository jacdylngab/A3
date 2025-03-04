# Set up the DB using the following commands:
# $ python
# > from app import db
# > db.create_all()
# > from models import User
# > admin = User(username='admin', email='admin@example.com')
# > db.session.add(admin)
# > db.session.commit()
# > User.query.all()

from app import db
from sqlalchemy import JSON


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    realname = db.Column(db.String(200), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    mailingaddress = db.Column(db.String(200), unique=False, nullable=False)
    creditcard = db.Column(db.String(20), unique=False, nullable=True)
    password = db.Column(db.String(200), unique=False, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    description = db.Column(db.String(200), unique=False, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)
    prod_image = db.Column(db.String(200), unique=False, nullable=False)

    def __repr__(self):
        return f"Product Name: {self.name}, Product Description: {self.description}, Product Price: {self.price}"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    realname = db.Column(db.String(200), unique=False, nullable=False)
    mailingaddress = db.Column(db.String(200), unique=False, nullable=False)
    cart = db.Column(JSON, nullable=False)
