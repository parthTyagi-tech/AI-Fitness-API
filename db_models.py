from flask_login import UserMixin
from datetime import datetime
from extensions import db


class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    results       = db.relationship('Result', backref='user', lazy=True)


class Result(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age               = db.Column(db.Integer)
    gender            = db.Column(db.String(10))
    height            = db.Column(db.Float)
    weight            = db.Column(db.Float)
    waist             = db.Column(db.Float)
    neck              = db.Column(db.Float)
    hip               = db.Column(db.Float)
    sleep             = db.Column(db.Float)
    workouts          = db.Column(db.Integer)
    calories          = db.Column(db.Float)
    activity          = db.Column(db.String(20))
    goal              = db.Column(db.String(20))
    exercise_location = db.Column(db.String(10))  # 'home' or 'gym'
    bf_pct            = db.Column(db.Float)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)


class UserProfile(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    age               = db.Column(db.Integer)
    gender            = db.Column(db.String(10))
    height            = db.Column(db.Float)
    activity          = db.Column(db.String(20))
    goal              = db.Column(db.String(20))
    exercise_location = db.Column(db.String(10))  # remembered for next visit
    user              = db.relationship('User', backref=db.backref('profile', uselist=False))
