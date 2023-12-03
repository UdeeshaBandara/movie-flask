from flask import Blueprint, render_template, request, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from .models import User, Movie
from .config import Config, db
from flask import request, jsonify, render_template
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

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            email = request.form.get('email')
            full_name = request.form.get('full_name')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            # Check if passwords match
            if password != confirm_password:
                return render_template('signup.html', message="Error: Passwords do not match")

            # Check if email already exists
            if User.objects(email=email):
                return render_template('signup.html', message="Error: Email already exists")

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(email=email, password=hashed_password, full_name=full_name)
            new_user.save()

            return render_template('signup.html', message="User registered successfully")

        return render_template('signup.html')


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            user = User.objects(email=email).first()

            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return render_template('login.html', message=f"Welcome, {user.full_name}! Login successful")
            else:
                return render_template('login.html', message="Error: Invalid email or password")

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return render_template('logout.html')
    
    @app.route('/movies/', methods=['GET'])
    def get_movies():
        movies = Movie.objects().to_json()
        return render_template('movies.html', movies=json_util.loads(movies))

    @app.route('/movies/<movie_id>', methods=['GET'])
    def get_movie(movie_id):
        try:
            movie_id = ObjectId(movie_id)
        except:
            return jsonify({"message": "Invalid movie ID format"}), 400

        movie = Movie.objects(id=movie_id).first()
        if movie:
            return render_template('movie_details.html', movie=json_util.dumps(movie))
        else:
            return jsonify({"message": "Movie not found"}), 404

    @app.route('/movies/add_new_movie/', methods=['GET', 'POST'])
    def add_new_movie():
        if request.method == 'POST':
            try:
                movie_data = {
                    "movie_name": request.form.get('movie_name'),
                    "movie_year": int(request.form.get('movie_year')),
                    "movie_rating": float(request.form.get('movie_rating')),
                    "user_votes": request.form.get('user_votes')
                }

                # Insert data into MongoDB
                new_movie = Movie(**movie_data)
                new_movie.save()

                success_message = "Movie added successfully!"
                return render_template('add_movie.html', success_message=success_message)

            except Exception as e:
                error_message = f"Error: {type(e).__name__} - {str(e)}"
                return render_template('add_movie.html', error_message=error_message)

        return render_template('add_movie.html')
        
    @app.route('/movies/<movie_id>/edit', methods=['GET', 'POST'])
    def edit_movie(movie_id):
        try:
            movie_id = ObjectId(movie_id)
        except:
            return jsonify({"message": "Invalid movie ID format"}), 400

        if request.method == 'GET':
            movie = Movie.objects(id=movie_id).first()
            if movie:
                return render_template('edit_movie.html', movie={
                    "id": str(movie.id),
                    "movie_name": movie.movie_name,
                    "movie_year": movie.movie_year,
                    "movie_rating": movie.movie_rating,
                    "user_votes": movie.user_votes
                })
            else:
                return jsonify({"message": "Movie not found"}), 404

        elif request.method == 'POST':
            # Handle the form submission for updating the movie
            updated_data = {
                "movie_name": request.form.get("movie_name"),
                "movie_year": int(request.form.get("movie_year")),
                "movie_rating": float(request.form.get("movie_rating")),
                "user_votes": request.form.get("user_votes")
            }

            movie = Movie.objects(id=movie_id).first()
            if movie:
                movie.modify(**updated_data)

                # Pass the success message to the template
                success_message = "Movie updated successfully"
                return render_template('edit_movie.html', movie={
                    "id": str(movie.id),
                    "movie_name": updated_data["movie_name"],
                    "movie_year": updated_data["movie_year"],
                    "movie_rating": updated_data["movie_rating"],
                    "user_votes": updated_data["user_votes"]
                }, success_message=success_message)
            else:
                return jsonify({"message": "Movie not found"}), 404

        else:
            return jsonify({"message": "Method not allowed"}), 405


    @app.route('/movies/<movie_id>/delete', methods=['POST', 'DELETE'])
    def delete_movie(movie_id):
        try:
            movie_id = ObjectId(movie_id)
        except Exception as e:
            return jsonify({"message": "Invalid movie ID format"}), 400

        if request.method == 'DELETE':
            movie = Movie.objects(id=movie_id).first()
            if movie:
                movie.delete()
                return jsonify({"message": "Movie deleted successfully!"}), 200
            else:
                return jsonify({"message": "Movie not found"}), 404
        elif request.method == 'POST':
            # Handle POST requests as needed
            return jsonify({"message": "Received POST request"}), 200
        else:
            return jsonify({"message": "Invalid request method"}), 400

    @app.route('/movies/<movie_id>')
    def view_movie(movie_id):
        movie = Movie.objects(id=movie_id).first()
        return render_template('delete_movie.html', movie=movie)
