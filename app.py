from flask import Flask, jsonify, request, render_template, url_for, redirect, flash
from datamanager.sqlite_data_manager import SQLiteDataManager
from datamanager.models import db
import os
from dotenv import load_dotenv
import requests
import re
import logging

# Load environment variables from .env file
load_dotenv()

# Base class for blueprints
class BlueprintBase:
    def __init__(self, app, data_manager, secret_key):
        self.app = app
        self.data_manager = data_manager
        self.secret_key = secret_key

    def init_app(self):
        self.register_routes()

# UsersBlueprint
class UsersBlueprint(BlueprintBase):
    def register_routes(self):
        @self.app.route('/')
        def home():
            return render_template('home.html')

        @self.app.route('/users')
        def users_list():
            try:
                users = self.data_manager.get_all_users()
                user_movies = {user.id: self.data_manager.get_user_movies(user.id) for user in users}
                return render_template('users_list.html', users=users, user_movies=user_movies)
            except Exception as e:
                self.app.logger.error(f"Error retrieving users: {str(e)}")
                flash("Error retrieving users. Please try again later.", "error")
                return render_template('users_list.html', users=[], user_movies={})

        @self.app.route('/add_user', methods=['GET', 'POST'])
        def add_user():
            if request.method == 'POST':
                try:
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
                except ValueError as e:
                    flash(str(e), "error")
                except Exception as e:
                    self.app.logger.error(f"Error adding user: {str(e)}")
                    flash("An unexpected error occurred. Please try again.", "error")

            return render_template('add_user.html')

        @self.app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
        def delete_user(user_id):
            try:
                self.data_manager.delete_user(user_id)
                flash("User deleted successfully!", "success")
            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                self.app.logger.error(f"Error deleting user {user_id}: {str(e)}")
                flash("An unexpected error occurred. Please try again.", "error")

            return redirect(url_for('users_list'))

# MoviesBlueprint
class MoviesBlueprint(BlueprintBase):
    def register_routes(self):
        @self.app.route('/users/<int:user_id>')
        def user_movies(user_id):
            try:
                movies = self.data_manager.get_user_movies(user_id)
                user = next((u for u in self.data_manager.get_all_users() if u.id == user_id), None)

                if not user:
                    flash("User not found!", "error")
                    return redirect(url_for('users_list'))

                return render_template('user_movies.html', user=user, movies=movies)
            except Exception as e:
                self.app.logger.error(f"Error retrieving movies for user {user_id}: {str(e)}")
                flash("Error retrieving movies. Please try again later.", "error")
                return redirect(url_for('users_list'))

        @self.app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
        def add_movie(user_id):
            if request.method == 'POST':
                movie_title = request.form.get('title', '').strip()

                if not movie_title:
                    flash("Movie title is required!", "error")
                    return render_template('add_movie.html', user_id=user_id)

                try:
                    movie_data = self._fetch_movie_data(movie_title)

                    if not movie_data:
                        flash("Movie not found on OMDb!", "error")
                        return render_template('add_movie.html', user_id=user_id)

                    existing_movie = self.data_manager.get_movie_by_id(movie_data['id'])

                    if not existing_movie:
                        self.data_manager.add_movie(movie_data)
                        existing_movie = movie_data

                    self.data_manager.add_favorite_movie(user_id, existing_movie['id'])
                    flash("Movie added successfully!", "success")
                    return redirect(url_for('user_movies', user_id=user_id))
                except Exception as e:
                    self.app.logger.error(f"Error adding movie: {str(e)}")
                    flash(f"Error adding movie: {str(e)}", "error")

            return render_template('add_movie.html', user_id=user_id)

        @self.app.route('/users/<int:user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
        def update_movie(user_id, movie_id):
            try:
                movie = next((m for m in self.data_manager.get_user_movies(user_id) if m.id == movie_id), None)

                if not movie:
                    flash("Movie not found!", "error")
                    return redirect(url_for('user_movies', user_id=user_id))

                if request.method == 'POST':
                    updated_data = {
                        'name': request.form.get('name', '').strip() or movie.name,
                        'director': request.form.get('director', '').strip() or movie.director,
                        'year': int(request.form.get('year') or movie.year),
                        'rating': float(request.form.get('rating') or movie.rating)
                    }

                    self.data_manager.update_movie(movie_id, updated_data)
                    flash("Movie updated successfully!", "success")
                    return redirect(url_for('user_movies', user_id=user_id))
            except (ValueError, AttributeError) as e:
                flash(f"Error updating movie: {str(e)}", "error")
            except Exception as e:
                self.app.logger.error(f"Error updating movie {movie_id}: {str(e)}")
                flash("An unexpected error occurred. Please try again.", "error")
                return redirect(url_for('user_movies', user_id=user_id))

            return render_template('update_movie.html', user_id=user_id, movie=movie)

        @self.app.route('/users/<int:user_id>/delete_movie/<movie_id>', methods=['GET', 'POST'])
        def delete_movie(user_id, movie_id):
            try:
                self.data_manager.delete_movie(movie_id)
                flash("Movie deleted successfully!", "success")
            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                self.app.logger.error(f"Error deleting movie {movie_id}: {str(e)}")
                flash("An unexpected error occurred. Please try again.", "error")

            return redirect(url_for('user_movies', user_id=user_id))

    def _fetch_movie_data(self, movie_title):
        omdb_api_key = self.app.config.get('OMDB_API_KEY')

        if not omdb_api_key:
            flash("OMDb API key not configured!", "error")
            return None

        try:
            response = requests.get(f"http://www.omdbapi.com/?t={movie_title}&apikey={omdb_api_key}", timeout=5)
            response.raise_for_status()

            data = response.json()

            if data.get('Response') != 'True':
                flash(f"Movie not found on OMDb: {data.get('Error', 'Unknown error')}", "error")
                return None

            year_str = data.get('Year', '0')
            year_match = re.search(r'^\d{4}', year_str)
            year = int(year_match.group(0)) if year_match else 0

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

# MovieWebApp
class MovieWebApp:
    def __init__(self, config=None):
        self.app = Flask(__name__)
        self.configure_app(config)
        self.initialize_database()
        self.register_blueprints()
        self.setup_logging()
        self.register_error_handlers()

    def configure_app(self, config=None):
        db_path = os.path.join(os.path.dirname(__file__), 'data', 'moviweb.db')
        default_config = {
            'SQLALCHEMY_DATABASE_URI': f"sqlite:///{db_path}",
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': os.getenv('SECRET_KEY', 'default_secret_key'),
            'DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't'),
            'OMDB_API_KEY': os.getenv('OMDB_API_KEY', '')
        }

        if config:
            default_config.update(config)

        for key, value in default_config.items():
            self.app.config[key] = value

    def initialize_database(self):
        db.init_app(self.app)
        self.data_manager = SQLiteDataManager(self.app, self.app.config['SQLALCHEMY_DATABASE_URI'])
        self.app.data_manager = self.data_manager
        with self.app.app_context():
            db.create_all()

    def register_blueprints(self):
        self.users_blueprint = UsersBlueprint(self.app, self.data_manager, self.app.config['SECRET_KEY'])
        self.movies_blueprint = MoviesBlueprint(self.app, self.data_manager, self.app.config['SECRET_KEY'])
        self.users_blueprint.init_app()
        self.movies_blueprint.init_app()

    def setup_logging(self):
        if not self.app.debug:
            handler = logging.FileHandler('app.log')
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.app.logger.addHandler(handler)
            self.app.logger.setLevel(logging.INFO)

    def register_error_handlers(self):
        @self.app.errorhandler(404)
        def page_not_found(e):
            return render_template('404.html'), 404

        @self.app.errorhandler(500)
        def internal_server_error(e):
            self.app.logger.error(f"Internal server error: {str(e)}")
            return render_template('500.html'), 500

        @self.app.errorhandler(403)
        def forbidden(e):
            return render_template('403.html', error=str(e)), 403

        @self.app.errorhandler(401)
        def unauthorized(e):
            return render_template('401.html', error=str(e)), 401

    def run(self, host='0.0.0.0', port=5002, debug=None):
        if debug is None:
            debug = self.app.config.get('DEBUG', False)
        self.app.run(debug=debug, host=host, port=port)

if __name__ == '__main__':
    movie_app = MovieWebApp()
    movie_app.run()
