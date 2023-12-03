from flask_mongoengine import Document

from .config import db

class User(Document):
    email = db.EmailField(unique=True, required=True)
    password = db.StringField(required=True)
    full_name = db.StringField()
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    meta = {
        'collection': 'users'  
    }

class Movie(Document):
    movie_name = db.StringField(required=True)
    movie_year = db.IntField(required=True)
    movie_rating = db.FloatField(required=True)
    user_votes = db.StringField()

    meta = {
        'collection': 'movies'  
    }
