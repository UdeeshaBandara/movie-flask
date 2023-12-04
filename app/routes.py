from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from .models import User, Movie
from .config import Config, db
from app import app, mongo
from bson import json_util, ObjectId
from bson.errors import InvalidId

main = Blueprint('main', __name__)
bcrypt = Bcrypt()
login_manager = LoginManager()
bcrypt.init_app(app)
login_manager.init_app(app)

def configure_routes():

    @login_manager.user_loader
    def load_user(user_id):
        return User.objects(pk=user_id).first()

    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.json
        email = data.get('email')
        full_name = data.get('full_name')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            return jsonify(message="Error: Passwords do not match"), 400

        # Check if email already exists
        if User.objects(email=email):
            return jsonify(message="Error: Email already exists"), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password=hashed_password, full_name=full_name)
        new_user.save()

        return jsonify(message="User registered successfully")

    @app.route('/login', methods=['POST'])
    def login():
        data = request.json
        email = data.get('email')
        password = data.get('password')

        user = User.objects(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return jsonify(message=f"Welcome, {user.full_name}! Login successful")

        return jsonify(message="Error: Invalid email or password"), 401

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return jsonify(message="Logout successful")

    @app.route('/movies/', methods=['GET'])
    def get_movies():
        movies = Movie.objects().to_json()
        parsed_movies = json_util.loads(movies)

        # Convert ObjectId to string for each document
        for movie in parsed_movies:
            movie['_id'] = str(movie['_id'])

        return jsonify(movies=parsed_movies)

    @app.route('/movies/<movie_id>', methods=['GET'])
    def get_movie(movie_id):
        try:
            movie_id = ObjectId(movie_id)
        except:
            return jsonify({"message": "Invalid movie ID format"}), 400

        movie = Movie.objects(id=movie_id).first()
        if movie:
            # Convert ObjectId to string for serialization
            movie_data = json_util.loads(movie.to_json())
            movie_data['_id'] = str(movie_data['_id'])
            return jsonify(movie=movie_data)
        else:
            return jsonify({"message": "Movie not found"}), 404

    @app.route('/movies/add_new_movie/', methods=['POST'])
    def add_new_movie():
        try:
            movie_data = {
                "movie_name": request.json.get('movie_name'),
                "movie_year": int(request.json.get('movie_year')),
                "movie_rating": float(request.json.get('movie_rating')),
                "user_votes": request.json.get('user_votes')
            }

            # Insert data into MongoDB
            new_movie = Movie(**movie_data)
            new_movie.save()

            success_message = "Movie added successfully!"
            return jsonify(success_message=success_message)

        except Exception as e:
            error_message = f"Error: {type(e).__name__} - {str(e)}"
            return jsonify(error_message=error_message), 400

    @app.route('/movies/<movie_id>/edit', methods=['POST'])
    def edit_movie(movie_id):
        try:
            movie_id = ObjectId(movie_id)
        except:
            return jsonify({"message": "Invalid movie ID format"}), 400

        # Handle the form submission for updating the movie
        updated_data = {
            "movie_name": request.json.get("movie_name"),
            "movie_year": int(request.json.get("movie_year")),
            "movie_rating": float(request.json.get("movie_rating")),
            "user_votes": request.json.get("user_votes")
        }

        movie = Movie.objects(id=movie_id).first()
        if movie:
            movie.modify(**updated_data)

            # Pass the success message to the template
            success_message = "Movie updated successfully"
            return jsonify(movie=updated_data, success_message=success_message)
        else:
            return jsonify({"message": "Movie not found"}), 404

    @app.route('/movies/<movie_id>/delete', methods=['DELETE'])
    def delete_movie(movie_id):
        try:
            movie_id = ObjectId(movie_id)
        except Exception as e:
            return jsonify({"message": "Invalid movie ID format"}), 400

        movie = Movie.objects(id=movie_id).first()
        if movie:
            movie.delete()
            return jsonify({"message": "Movie deleted successfully!"}), 200
        else:
            return jsonify({"message": "Movie not found"}), 404

    @app.route('/movies/<movie_id>')
    def view_movie(movie_id):
        movie = Movie.objects(id=movie_id).first()
        return jsonify(movie=json_util.loads(movie.to_json()))
