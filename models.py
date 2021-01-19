from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import orm
from project.utils.mail_helper import send_mail
from . import db


class Following(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('website.id', ondelete="CASCADE"), primary_key=True)
    send_mail = db.Column(db.Boolean)
    user = db.relationship("User", back_populates="websites")
    website = db.relationship("Website", back_populates="users")

    def __repr__(self):
        return str(str(self.user) + str(self.website))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    websites = db.relationship("Following", back_populates="user")

    def __repr__(self):
        return self.name

    def update(self, webpage):
        print("user notified")
        send_mail(self.email, webpage)


class Website(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), unique=True)
    users = db.relationship("Following", back_populates="website", cascade="all, delete", passive_deletes=True)
    status = db.relationship('WebsiteStatus', backref='website', cascade="all, delete", passive_deletes=True)
    attack = db.Column(db.Boolean, default=False)

    def __init__(self):
        self.observers = []

    @orm.reconstructor
    def init_on_load(self):
        self.observers = [x.user for x in self.users if x.send_mail is True]

    def __repr__(self):
        return self.url

    def notify(self):
        for observer in self.observers:
            observer.update(self)

    def detach(self, observer):
        self.observers.remove(observer)

    def attach(self, observer):
        self.observers.append(observer)


class WebsiteStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    alive = db.Column(db.Boolean)
    latency = db.Column(db.Integer, nullable=True)
    website_id = db.Column(db.Integer, db.ForeignKey('website.id', ondelete="CASCADE"))

    def __repr__(self):
        return str(str(self.timestamp) + str(self.latency))
