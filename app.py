"""Flask application for managing users and their favorite movies."""

from flask import Flask, jsonify, request, render_template, url_for, redirect, flash
from datamanager.sqlite_data_manager import SQLiteDataManager
from datamanager.models import db
import os
from dotenv import load_dotenv
import requests
import re
import logging
from functools import wraps

# Load environment variables from .env file
load_dotenv()


def handle_errors(f):
    """Decorator to handle common exceptions in routes.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function with error handling.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            app = Flask.current_app
            app.logger.error(f"Error in {f.__name__}: {str(e)}")
            flash("An unexpected error occurred. Please try again.", "error")

        # Default fallback - return to previous page or home
        return redirect(request.referrer or url_for('home'))

    return decorated_function


class BlueprintBase:
    """Base class for blueprints."""

    def __init__(self, app, data_manager):
        """Initialize the blueprint.

        Args:
            app (Flask): The Flask application instance.
            data_manager (SQLiteDataManager): The data manager instance.
        """
        self.app = app
        self.data_manager = data_manager

    def init_app(self):
        """Initialize the blueprint by registering routes."""
        self.register_routes()


class UsersBlueprint(BlueprintBase):
    """Blueprint for user-related routes."""

    def register_routes(self):
        """Register user-related routes."""

        @self.app.route('/')
        def home():
            """Render the home page."""
            return render_template('home.html')

        @self.app.route('/users')
        @handle_errors
        def users_list():
            """Render the list of users and their movies."""
            users = self.data_manager.get_all_users()
            user_movies = {user.id: self.data_manager.get_user_movies(user.id) for user in users}
            return render_template('users_list.html', users=users, user_movies=user_movies)

        @self.app.route('/add_user', methods=['GET', 'POST'])
        @handle_errors
        def add_user():
            """Add a new user."""
            if request.method == 'POST':
                user_data = {
                    'id': int(request.form['id']),
                    'name': request.form['name'].strip()
                }

                if not user_data['name']:
                    flash("User name is required!", "error")
                    return render_template('add_user.html')

                self.data_manager.add_user(user_data)
                flash("User added successfully!", "success")
                return redirect(url_for('users_list'))

            return render_template('add_user.html')

        @self.app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
        @handle_errors
        def delete_user(user_id):
            """Delete a user by ID."""
            self.data_manager.delete_user(user_id)
            flash("User deleted successfully!", "success")
            return redirect(url_for('users_list'))


class MoviesBlueprint(BlueprintBase):
    """Blueprint for movie-related routes."""

    def register_routes(self):
        """Register movie-related routes."""

        @self.app.route('/users/<int:user_id>')
        @handle_errors
        def user_movies(user_id):
            """Render the list of movies for a specific user."""
            movies = self.data_manager.get_user_movies(user_id)
            user = next((u for u in self.data_manager.get_all_users() if u.id == user_id), None)

            if not user:
                flash("User not found!", "error")
                return redirect(url_for('users_list'))

            return render_template('user_movies.html', user=user, movies=movies)

        @self.app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
        @handle_errors
        def add_movie(user_id):
            """Add a movie to a user's favorites."""
            if request.method == 'POST':
                movie_title = request.form.get('title', '').strip()

                if not movie_title:
                    flash("Movie title is required!", "error")
                    return render_template('add_movie.html', user_id=user_id)

                movie_data = self._fetch_movie_data(movie_title)

                if not movie_data:
                    return render_template('add_movie.html', user_id=user_id)

                try:
                    # Check if movie already exists in database
                    existing_movie = self.data_manager.get_movie_by_id(movie_data['id'])

                    # Get the movie ID to use
                    if existing_movie:
                        # If existing_movie is an object with an id attribute
                        if hasattr(existing_movie, 'id'):
                            movie_id = existing_movie.id
                        # If existing_movie is a dictionary with an 'id' key
                        elif isinstance(existing_movie, dict) and 'id' in existing_movie:
                            movie_id = existing_movie['id']
                        else:
                            # Log the type for debugging
                            self.app.logger.error(f"Unexpected existing_movie type: {type(existing_movie)}")
                            movie_id = str(existing_movie)  # Convert to string as fallback
                    else:
                        # Add new movie to database
                        self.data_manager.add_movie(movie_data)
                        movie_id = movie_data['id']

                    # Check if user already has this movie in favorites
                    user_movies = self.data_manager.get_user_movies(user_id)

                    # Convert movie_id to string for consistent comparison
                    movie_id_str = str(movie_id)

                    if any(str(movie.id) == movie_id_str for movie in user_movies):
                        flash("This movie is already in your favorites!", "info")
                    else:
                        # Add to user's favorites
                        self.data_manager.add_favorite_movie(user_id, movie_id)
                        flash("Movie added successfully to your favorites!", "success")

                    return redirect(url_for('user_movies', user_id=user_id))

                except Exception as e:
                    self.app.logger.error(f"Error in add_movie: {str(e)}")
                    flash(f"Error adding movie: {str(e)}", "error")
                    return render_template('add_movie.html', user_id=user_id)

            return render_template('add_movie.html', user_id=user_id)

        @self.app.route('/users/<int:user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
        @handle_errors
        def update_movie(user_id, movie_id):
            """Update a movie in a user's favorites."""
            # Get the movie from the user's collection
            user_movies = self.data_manager.get_user_movies(user_id)
            movie = next((m for m in user_movies if str(m.id) == str(movie_id)), None)

            if not movie:
                flash("Movie not found in user's collection!", "error")
                return redirect(url_for('user_movies', user_id=user_id))

            if request.method == 'POST':
                try:
                    # Get form data with proper type conversion and fallbacks
                    name = request.form.get('name', '').strip()
                    director = request.form.get('director', '').strip()

                    # Handle year with proper validation
                    year_str = request.form.get('year', '')
                    try:
                        year = int(year_str) if year_str else movie.year
                    except ValueError:
                        year = movie.year
                        flash("Invalid year format. Using original value.", "warning")

                    # Handle rating with proper validation
                    rating_str = request.form.get('rating', '')
                    try:
                        rating = float(rating_str) if rating_str else movie.rating
                    except ValueError:
                        rating = movie.rating
                        flash("Invalid rating format. Using original value.", "warning")

                    # Create updated data dictionary
                    updated_data = {
                        'name': name or movie.name,
                        'director': director or movie.director,
                        'year': year,
                        'rating': rating
                    }

                    # Log the update operation for debugging
                    self.app.logger.info(f"Updating movie {movie_id} with data: {updated_data}")

                    # Update the movie in the database
                    self.data_manager.update_movie(movie_id, updated_data)

                    flash("Movie updated successfully!", "success")
                    return redirect(url_for('user_movies', user_id=user_id))

                except Exception as e:
                    self.app.logger.error(f"Error updating movie {movie_id}: {str(e)}")
                    flash(f"Error updating movie: {str(e)}", "error")
                    # Re-render the form with the current data
                    return render_template('update_movie.html', user_id=user_id, movie=movie)

            # GET request - show the update form
            return render_template('update_movie.html', user_id=user_id, movie=movie)

        @self.app.route('/users/<int:user_id>/delete_movie/<movie_id>', methods=['GET', 'POST'])
        @handle_errors
        def delete_movie(user_id, movie_id):
            """Delete a movie from a user's favorites."""
            self.data_manager.delete_movie(movie_id)
            flash("Movie deleted successfully!", "success")
            return redirect(url_for('user_movies', user_id=user_id))

    def _fetch_movie_data(self, movie_title):
        """Fetch movie data from OMDb API.

        Args:
            movie_title (str): The title of the movie to fetch.

        Returns:
            dict: The movie data or None if not found.
        """
        omdb_api_key = self.app.config.get('OMDB_API_KEY')

        if not omdb_api_key:
            flash("OMDb API key not configured!", "error")
            return None

        try:
            response = requests.get(
                f"http://www.omdbapi.com/?t={movie_title}&apikey={omdb_api_key}",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            if data.get('Response') != 'True':
                flash(f"Movie not found on OMDb: {data.get('Error', 'Unknown error')}", "error")
                return None

            # Extract year (first 4 digits)
            year_str = data.get('Year', '0')
            year_match = re.search(r'^\d{4}', year_str)
            year = int(year_match.group(0)) if year_match else 0

            # Parse rating
            rating_str = data.get('imdbRating', 'N/A')
            rating = float(rating_str) if rating_str != 'N/A' else 0.0

            return {
                'id': data.get('imdbID', ''),
                'name': data.get('Title', ''),
                'director': data.get('Director', ''),
                'year': year,
                'rating': rating,
                'poster': data.get('Poster', '')
            }
        except requests.RequestException as e:
            self.app.logger.error(f"Error fetching movie from OMDb: {str(e)}")
            flash(f"Error fetching movie details from OMDb: {str(e)}", "error")
            return None


class MovieWebApp:
    """Main application class for the movie web app."""

    def __init__(self, config=None):
        """Initialize the application.

        Args:
            config (dict, optional): Configuration dictionary. Defaults to None.
        """
        self.app = Flask(__name__)
        self.configure_app(config)
        self.initialize_database()
        self.register_blueprints()
        self.setup_logging()
        self.register_error_handlers()

    def configure_app(self, config=None):
        """Configure the Flask application.

        Args:
            config (dict, optional): Configuration dictionary. Defaults to None.
        """
        db_path = os.path.join(os.path.dirname(__file__), 'data', 'moviweb.db')
        default_config = {
            'SQLALCHEMY_DATABASE_URI': f"sqlite:///{db_path}",
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': os.getenv('SECRET_KEY', 'default_secret_key'),
            'DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't'),
            'OMDB_API_KEY': os.getenv('OMDB_API_KEY', '')
        }

        self.app.config.update(default_config)
        if config:
            self.app.config.update(config)

    def initialize_database(self):
        """Initialize the database."""
        db.init_app(self.app)
        self.data_manager = SQLiteDataManager(self.app, self.app.config['SQLALCHEMY_DATABASE_URI'])
        self.app.data_manager = self.data_manager
        with self.app.app_context():
            db.create_all()

    def register_blueprints(self):
        """Register blueprints."""
        self.users_blueprint = UsersBlueprint(self.app, self.data_manager)
        self.movies_blueprint = MoviesBlueprint(self.app, self.data_manager)
        self.users_blueprint.init_app()
        self.movies_blueprint.init_app()

    def setup_logging(self):
        """Set up logging for the application."""
        if not self.app.debug:
            handler = logging.FileHandler('app.log')
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.app.logger.addHandler(handler)
            self.app.logger.setLevel(logging.INFO)

    def register_error_handlers(self):
        """Register error handlers."""

        @self.app.errorhandler(404)
        def page_not_found(e):
            """Handle 404 errors."""
            return render_template('404.html'), 404

        @self.app.errorhandler(500)
        def internal_server_error(e):
            """Handle 500 errors."""
            self.app.logger.error(f"Internal server error: {str(e)}")
            return render_template('500.html'), 500

        @self.app.errorhandler(403)
        def forbidden(e):
            """Handle 403 errors."""
            return render_template('403.html', error=str(e)), 403

        @self.app.errorhandler(401)
        def unauthorized(e):
            """Handle 401 errors."""
            return render_template('401.html', error=str(e)), 401

    def run(self, host='0.0.0.0', port=5002, debug=None):
        """Run the application.

        Args:
            host (str, optional): The host to run the app on. Defaults to '0.0.0.0'.
            port (int, optional): The port to run the app on. Defaults to 5002.
            debug (bool, optional): Whether to run in debug mode. Defaults to None.
        """
        if debug is None:
            debug = self.app.config.get('DEBUG', False)
        self.app.run(debug=debug, host=host, port=port)


if __name__ == '__main__':
    movie_app = MovieWebApp()
    movie_app.run()
