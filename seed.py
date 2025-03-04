from datamanager.models import db
from flask import Flask
import requests
import os

def create_app(config=None):
    app = Flask(__name__)

    # Default configuration
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'moviweb.db')
    default_config = {
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{db_path}",
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': os.getenv('SECRET_KEY', 'default_secret_key'),
        'DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't'),
        'OMDB_API_KEY': os.getenv('OMDB_API_KEY', '')
    }

    # Override defaults with any provided config
    if config:
        default_config.update(config)

    # Apply configuration to app
    for key, value in default_config.items():
        app.config[key] = value

    # Initialize the database
    from datamanager.sqlite_data_manager import SQLiteDataManager  # Ensure this import is correct
    db.init_app(app)
    data_manager = SQLiteDataManager(app, app.config['SQLALCHEMY_DATABASE_URI'])
    app.data_manager = data_manager

    return app  # Return the app object


def fetch_poster_from_omdb(title, api_key):
    """
    Fetches the poster URL for a movie from the OMDb API.
    :param title: Movie title
    :param api_key: OMDb API key
    :return: Poster URL or 'N/A' if not found
    """
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if data.get('Response') == 'True':
            return data.get('Poster', 'N/A')
        else:
            print(f"Error fetching poster for {title}: {data.get('Error', 'Unknown error')}")
            return 'N/A'
    except requests.RequestException as e:
        print(f"Error fetching poster for {title}: {e}")
        return 'N/A'


def seed_database(app, data_manager):
    """
    Seeds the database with sample users and movies, fetching posters from OMDb.
    """
    print("Seeding the database...")

    # Add sample users
    users_data = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
        {'id': 3, 'name': 'Charlie'}
    ]
    for user_data in users_data:
        try:
            data_manager.add_user(user_data)
            print(f"Added user: {user_data['name']}")
        except ValueError as e:
            print(f"Error adding user: {e}")

    # Add sample movies
    movies_data = [
        {'id': 101, 'name': 'Inception', 'director': 'Christopher Nolan', 'year': 2010, 'rating': 8.7},
        {'id': 102, 'name': 'Interstellar', 'director': 'Christopher Nolan', 'year': 2014, 'rating': 8.6},
        {'id': 103, 'name': 'The Dark Knight', 'director': 'Christopher Nolan', 'year': 2008, 'rating': 9.0},
        {'id': 104, 'name': 'Avatar', 'director': 'James Cameron', 'year': 2009, 'rating': 7.8},
        {'id': 105, 'name': 'Titanic', 'director': 'James Cameron', 'year': 1997, 'rating': 7.8}
    ]

    omdb_api_key = app.config.get('OMDB_API_KEY')
    if not omdb_api_key:
        print("OMDb API key not configured!")
        return

    for movie_data in movies_data:
        try:
            # Fetch the poster URL from OMDb
            poster_url = fetch_poster_from_omdb(movie_data['name'], omdb_api_key)
            movie_data['poster'] = poster_url

            # Add the movie to the database
            data_manager.add_movie(movie_data)
            print(f"Added movie: {movie_data['name']} (Poster: {poster_url})")
        except ValueError as e:
            print(f"Error adding movie: {e}")

    # Add favorite movies for users
    try:
        data_manager.add_favorite_movie(1, 101)  # Alice likes Inception
        data_manager.add_favorite_movie(1, 102)  # Alice likes Interstellar
        data_manager.add_favorite_movie(2, 103)  # Bob likes The Dark Knight
        data_manager.add_favorite_movie(3, 104)  # Charlie likes Avatar
        data_manager.add_favorite_movie(3, 105)  # Charlie likes Titanic
        print("Added favorite movies for users.")
    except Exception as e:
        print(f"Error adding favorite movies: {e}")


if __name__ == '__main__':
    # Create the Flask app and data manager
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()  # Clear existing data
        db.create_all()  # Recreate tables

        # Seed the database
        data_manager = app.data_manager
        seed_database(app, data_manager)

    print("Database seeding complete!")