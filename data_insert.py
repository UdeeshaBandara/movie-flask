from flask import Flask
from flask_pymongo import PyMongo
from bson.json_util import loads
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/local"
app.config['METHOD_OVERRIDE'] = True

mongo = PyMongo(app)

def insert_movies():
    try:
        # Load movie data from JSON file
        with open("movie_data.json", "r") as file:
            movie_data = json.load(file)

        # Insert data into MongoDB
        result = mongo.db.movies.insert_many(loads(json.dumps(movie_data)))

        print(f"Inserted {len(result.inserted_ids)} movies.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    insert_movies()
