from datetime import datetime
import secrets
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'user'

    id              = Column(Integer, primary_key=True)
    name            = Column(String(100), nullable=False)
    email           = Column(String(150), unique=True, nullable=False, index=True)
    password_hash   = Column(String(200), nullable=True)   # nullable for Google OAuth users
    google_id       = Column(String(200), unique=True, nullable=True)
    referral_code   = Column(String(16), unique=True, nullable=False, default=lambda: secrets.token_hex(8))
    referred_by     = Column(Integer, ForeignKey('user.id'), nullable=True)
    referral_count  = Column(Integer, default=0)

    results         = relationship('Result', back_populates='user', cascade='all, delete-orphan')
    profile         = relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> str:
        return str(self.id)


class AnonymousUser:
    id = None
    name = "Guest"
    email = ""

    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def is_active(self) -> bool:
        return False

    @property
    def is_anonymous(self) -> bool:
        return True

    def get_id(self):
        return None


class Result(Base):
    __tablename__ = 'result'

    id                = Column(Integer, primary_key=True)
    user_id           = Column(Integer, ForeignKey('user.id'), nullable=False)
    age               = Column(Integer)
    gender            = Column(String(10))
    height            = Column(Float)
    weight            = Column(Float)
    waist             = Column(Float)
    neck              = Column(Float)
    hip               = Column(Float)
    sleep             = Column(Float)
    workouts          = Column(Integer)
    calories          = Column(Float)
    activity          = Column(String(20))
    goal              = Column(String(20))
    exercise_location = Column(String(10))  # 'home' or 'gym'
    bf_pct            = Column(Float)
    created_at        = Column(DateTime, default=datetime.utcnow)

    user              = relationship('User', back_populates='results')


class UserProfile(Base):
    __tablename__ = 'user_profile'

    id                = Column(Integer, primary_key=True)
    user_id           = Column(Integer, ForeignKey('user.id'), unique=True, nullable=False)
    age               = Column(Integer)
    gender            = Column(String(10))
    height            = Column(Float)
    activity          = Column(String(20))
    goal              = Column(String(20))
    exercise_location = Column(String(10))  # remembered for next visit

    user              = relationship('User', back_populates='profile')
