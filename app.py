from flask import Flask, jsonify, request, render_template, url_for, redirect, flash
from datamanager.sqlite_data_manager import SQLiteDataManager
from datamanager.models import db
import os
from dotenv import load_dotenv  # Import dotenv for loading environment variables
import requests
import re

# Load environment variables from .env file
load_dotenv()


class MovieWebApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.configure_app()  # Configure the Flask app
        self.initialize_database()  # Initialize the database and attach the data manager
        self.register_routes()  # Register all routes for the Flask app

    def configure_app(self):
        """Configure the Flask app."""
        db_path = os.path.join(os.path.dirname(__file__), 'data', 'moviweb.db')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.secret_key = 'your_secret_key'  # For flash messages

    def initialize_database(self):
        """Initialize the database and attach the data manager."""
        db.init_app(self.app)
        self.data_manager = SQLiteDataManager(self.app, self.app.config['SQLALCHEMY_DATABASE_URI'])
        self.app.data_manager = self.data_manager
        with self.app.app_context():
            db.create_all()  # Create tables if they don't exist

    def register_routes(self):
        """Register all routes for the Flask app."""

        @self.app.route('/')
        def home():
            """Home page route."""
            return render_template('home.html')

        @self.app.route('/users')
        def users_list():
            """Display a list of all users."""
            users = self.data_manager.get_all_users()
            user_movies = {}
            for user in users:
                user_movies[user.id] = self.data_manager.get_user_movies(user.id)
            return render_template('users_list.html', users=users, user_movies=user_movies)

        @self.app.route('/users/<int:user_id>')
        def user_movies(user_id):
            """Display the list of movies for a specific user."""
            movies = self.data_manager.get_user_movies(user_id)
            user = next((u for u in self.data_manager.get_all_users() if u.id == user_id), None)
            if not user:
                flash("User not found!", "error")
                return redirect(url_for('users_list'))
            return render_template('user_movies.html', user=user, movies=movies)

        @self.app.route('/add_user', methods=['GET', 'POST'])
        def add_user():
            """Add a new user."""
            if request.method == 'POST':
                user_data = {
                    'id': int(request.form['id']),
                    'name': request.form['name']
                }
                try:
                    self.data_manager.add_user(user_data)
                    flash("User added successfully!", "success")
                    return redirect(url_for('users_list'))
                except ValueError as e:
                    flash(str(e), "error")
            return render_template('add_user.html')

        @self.app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
        def add_movie(user_id):
            """Add a new movie to a user's favorites."""
            if request.method == 'POST':
                movie_title = request.form.get('title')
                if not movie_title:
                    flash("Movie title is required!", "error")
                    return render_template('add_movie.html', user_id=user_id)

                # Fetch OMDb API key from environment variables
                omdb_api_key = os.getenv('OMDB_API_KEY')
                if not omdb_api_key:
                    flash("OMDb API key not configured!", "error")
                    return redirect(url_for('user_movies', user_id=user_id))

                # Fetch movie details from OMDb API
                response = requests.get(f"http://www.omdbapi.com/?t={movie_title}&apikey={omdb_api_key}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('Response') == 'True':
                        year_str = data.get('Year', '0')
                        year_match = re.search(r'^\d{4}', year_str)
                        default_year = int(year_match.group(0)) if year_match else 0
                        rating_str = data.get('imdbRating', 'N/A')
                        default_rating = float(rating_str) if rating_str != 'N/A' else 0.0

                        movie_data = {
                            'id': data.get('imdbID', ''),
                            'name': data.get('Title', ''),
                            'director': data.get('Director', ''),
                            'year': default_year,
                            'rating': default_rating
                        }

                        form_name = request.form.get('name', '').strip()
                        form_director = request.form.get('director', '').strip()
                        form_year = request.form.get('year', '').strip()
                        form_rating = request.form.get('rating', '').strip()

                        if form_name:
                            movie_data['name'] = form_name
                        if form_director:
                            movie_data['director'] = form_director
                        if form_year:
                            movie_data['year'] = int(form_year)
                        if form_rating:
                            movie_data['rating'] = float(form_rating)

                        self.data_manager.add_movie(movie_data)
                        self.data_manager.add_favorite_movie(user_id, movie_data['id'])
                        flash("Movie added successfully!", "success")
                        return redirect(url_for('user_movies', user_id=user_id))
                    else:
                        flash("Movie not found on OMDb!", "error")
                else:
                    flash("Error fetching movie details from OMDb!", "error")
            return render_template('add_movie.html', user_id=user_id)

        @self.app.route('/users/<int:user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
        def update_movie(user_id, movie_id):
            """Update a movie's details."""
            if request.method == 'POST':
                updated_data = {
                    'name': request.form.get('name'),
                    'director': request.form.get('director'),
                    'year': request.form.get('year'),
                    'rating': request.form.get('rating')
                }
                try:
                    self.data_manager.update_movie(movie_id, updated_data)
                    flash("Movie updated successfully!", "success")
                    return redirect(url_for('user_movies', user_id=user_id))
                except ValueError as e:
                    flash(str(e), "error")

            # Fetch current movie details for pre-filling the form
            movie = next((m for m in self.data_manager.get_user_movies(user_id) if m.id == movie_id), None)
            if not movie:
                flash("Movie not found!", "error")
                return redirect(url_for('user_movies', user_id=user_id))
            return render_template('update_movie.html', user_id=user_id, movie=movie)

        @self.app.route('/users/<int:user_id>/delete_movie/<movie_id>', methods=['GET', 'POST'])
        def delete_movie(user_id, movie_id):
            """Delete a movie from a user's favorites."""
            try:
                self.data_manager.delete_movie(movie_id)
                flash("Movie deleted successfully!", "success")
            except ValueError as e:
                flash(str(e), "error")
            return redirect(url_for('user_movies', user_id=user_id))

        @self.app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
        def delete_user(user_id):
            """Delete a user."""
            try:
                self.data_manager.delete_user(user_id)
                flash("User deleted successfully!", "success")
            except ValueError as e:
                flash(str(e), "error")
            return redirect(url_for('users_list'))

        @self.app.errorhandler(404)
        def page_not_found(e):
            return render_template('404.html'), 404

        @self.app.errorhandler(500)
        def internal_server_error(e):
            return render_template('500.html'), 500

        @self.app.errorhandler(403)
        def forbidden(e):
            """Handle 403 Forbidden errors."""
            return render_template('403.html', error=str(e)), 403

        @self.app.errorhandler(401)
        def unauthorized(e):
            """Handle 401 Unauthorized errors."""
            return render_template('401.html', error=str(e)), 401


if __name__ == '__main__':
    app = MovieWebApp().app
    app.run(debug=True, host='0.0.0.0', port=5001)