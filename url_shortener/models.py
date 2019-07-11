import string
from datetime import datetime, date
from random import choices
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(512))
    short_url = db.Column(db.String(3), unique=True)
    visits = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now)
    has_password = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128))
    expiration_date = db.Column(db.DateTime, default=date.max)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_short_link(self, requested):
        if not self.query.filter_by(short_url=requested).first() and requested != "":
            self.short_url = requested
            return requested, True

        characters = string.digits + string.ascii_letters
        short_url = ''.join(choices(characters, k=3))

        link = self.query.filter_by(short_url=short_url).first()

        if link:
            return self.generate_short_link(""), requested == ""
        self.short_url = short_url
        return short_url, requested == ""

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.has_password = True

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_expdate(self, date):
        self.expiration_date = date
