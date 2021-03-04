from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from glimpses import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=True)
    isPassSet = db.Column(db.Boolean)

    def set_password(self, password):
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<User {}>".format(self.name)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return "<Category %r>" % self.name


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False)
    is_starred = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    length = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    category = db.relationship("Category", backref=db.backref("posts", lazy=True))

    def __repr__(self):
        return "<Post %r>" % self.title
