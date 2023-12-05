from flask import Flask
from flask_mongoengine import MongoEngine
import secrets

secret_key = secrets.token_hex(16)

class Config:
    MONGO_URI = "mongodb+srv://sktech_123:abcd1234@cluster0.3haue2p.mongodb.net/movie"
    SECRET_KEY = secret_key

app = Flask(__name__)
app.config.from_object(Config)

db = MongoEngine(app)
