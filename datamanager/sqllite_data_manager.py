# datamanager/sqlite_data_manager.py

from flask_sqlalchemy import SQLAlchemy
from .data_manager_interface import DataManagerInterface
from .models import db, User, Movie

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app, db_uri):
        self.app = app
        self.db_uri = db_uri
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    def get_all_users(self):
        with self.app.app_context():
            return db.session.query(User).all()

    def get_user_movies(self, user_id):
        with self.app.app_context():
            user = db.session.query(User).get(user_id)
            if user:
                return user.favorite_movies
            return []

    def add_user(self, user_data):
        with self.app.app_context():
            new_user = User(id=user_data.get('id'), name=user_data.get('name'))
            db.session.add(new_user)
            db.session.commit()

    def add_movie(self, movie_data):
        with self.app.app_context():
            new_movie = Movie(
                id=movie_data.get('id'),
                name=movie_data.get('name'),
                director=movie_data.get('director'),
                year=movie_data.get('year'),
                rating=movie_data.get('rating')
            )
            db.session.add(new_movie)
            db.session.commit()

    def update_movie(self, movie_id, updated_data):
        with self.app.app_context():
            movie = db.session.query(Movie).get(movie_id)
            if movie:
                movie.name = updated_data.get('name', movie.name)
                movie.director = updated_data.get('director', movie.director)
                movie.year = updated_data.get('year', movie.year)
                movie.rating = updated_data.get('rating', movie.rating)
                db.session.commit()
            else:
                raise ValueError(f"Movie with ID {movie_id} does not exist.")

    def delete_movie(self, movie_id):
        with self.app.app_context():
            movie = db.session.query(Movie).get(movie_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()
            else:
                raise ValueError(f"Movie with ID {movie_id} does not exist.")

    def delete_user(self, user_id):
        """Delete a user from the database."""
        with self.app.app_context():
            user = db.session.query(User).get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
            else:
                raise ValueError(f"User with ID {user_id} does not exist.")

    def update_user(self, user_id, updated_data):
        """Update an existing user in the database."""
        with self.app.app_context():
            user = db.session.query(User).get(user_id)
            if user:
                user.name = updated_data.get('name', user.name)
                db.session.commit()
            else:
                raise ValueError(f"User with ID {user_id} does not exist.")

    def add_favorite_movie(self, user_id, movie_id):
        """Add a movie to a user's favorites."""
        with self.app.app_context():
            user = db.session.query(User).get(user_id)
            movie = db.session.query(Movie).get(movie_id)
            if user and movie:
                if movie not in user.favorite_movies:
                    user.favorite_movies.append(movie)
                    db.session.commit()
                    print(f"Added movie {movie.name} to user {user.name}'s favorites.")
                else:
                    print(f"Movie {movie.name} is already in user {user.name}'s favorites.")
            else:
                raise ValueError(f"User or Movie not found.")