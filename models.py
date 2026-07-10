from datetime import datetime
from flask_login import UserMixin
from ext import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    author = db.Column(db.String())
    price = db.Column(db.Float())
    image = db.Column(db.String())
    desc = db.Column(db.Text())
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

    reviews = db.relationship("Review", backref="book", cascade="all, delete-orphan")


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    reviews = db.relationship("Review", backref="author", cascade="all, delete-orphan")


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text(), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    book_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
