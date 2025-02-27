from .data_manager_interface import DataManagerInterface
from .models import db, User, Movie


class SQLiteDataManager(DataManagerInterface):
    """
    A class that implements the DataManagerInterface using SQLite as the database backend.
    """

    def __init__(self, app, db_uri):
        """
        Initialize the SQLiteDataManager with a Flask app and database URI.
        Configures the SQLAlchemy database connection.

        Args:
            app (Flask): The Flask application instance.
            db_uri (str): The database URI for SQLite.
        """
        # Initialize the Flask app and configure the database connection
        self.app = app
        self.db_uri = db_uri
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    def get_all_users(self):
        """
        Retrieve all users from the database.

        Returns:
            list: A list of User objects.
        """
        # Query all users from the database
        with self.app.app_context():
            return db.session.query(User).all()

    def get_user_movies(self, user_id):
        """
        Retrieve all movies associated with a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of Movie objects associated with the user.
        """
        # Fetch the user and their favorite movies
        with self.app.app_context():
            user = db.session.query(User).get(user_id)
            if user:
                return user.favorite_movies
            return []

    def add_user(self, user_data):
        """
        Add a new user to the database.

        Args:
            user_data (dict): A dictionary containing user data (id, name).

        Raises:
            ValueError: If user data is invalid or missing.
        """
        # Create and add a new user to the database
        with self.app.app_context():
            new_user = User(
                id=user_data.get('id'),
                name=user_data.get('name')
            )
            db.session.add(new_user)
            db.session.commit()

    def add_movie(self, movie_data):
        """
        Add a new movie to the database.

        Args:
            movie_data (dict): A dictionary containing movie data (id, name, director, year, rating).

        Raises:
            ValueError: If movie data is invalid or missing.
        """
        # Create and add a new movie to the database
        with self.app.app_context():
            new_movie = Movie(
                id=movie_data.get('id'),  # Accept string ID
                name=movie_data.get('name'),
                director=movie_data.get('director'),
                year=movie_data.get('year'),
                rating=movie_data.get('rating')
            )
            db.session.add(new_movie)
            db.session.commit()

    def update_movie(self, movie_id, updated_data):
        """
        Update an existing movie in the database.

        Args:
            movie_id (int): The ID of the movie to update.
            updated_data (dict): A dictionary containing updated movie data.

        Raises:
            ValueError: If the movie does not exist.
        """
        # Update the movie's details in the database
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
        """
        Delete a movie from the database.

        Args:
            movie_id (int): The ID of the movie to delete.

        Raises:
            ValueError: If the movie does not exist.
        """
        # Delete the movie from the database
        with self.app.app_context():
            movie = db.session.query(Movie).get(movie_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()
            else:
                raise ValueError(f"Movie with ID {movie_id} does not exist.")

    def delete_user(self, user_id):
        """
        Delete a user from the database.

        Args:
            user_id (int): The ID of the user to delete.

        Raises:
            ValueError: If the user does not exist.
        """
        # Delete the user from the database
        with self.app.app_context():
            user = db.session.query(User).get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
            else:
                raise ValueError(f"User with ID {user_id} does not exist.")

    def update_user(self, user_id, updated_data):
        """
        Update an existing user in the database.

        Args:
            user_id (int): The ID of the user to update.
            updated_data (dict): A dictionary containing updated user data.

        Raises:
            ValueError: If the user does not exist.
        """
        # Update the user's details in the database
        with self.app.app_context():
            user = db.session.query(User).get(user_id)
            if user:
                user.name = updated_data.get('name', user.name)
                db.session.commit()
            else:
                raise ValueError(f"User with ID {user_id} does not exist.")

    def add_favorite_movie(self, user_id, movie_id):
        """
        Add a movie to a user's favorites.

        Args:
            user_id (int): The ID of the user.
            movie_id (int): The ID of the movie.

        Raises:
            ValueError: If the user or movie does not exist.
        """
        # Add the movie to the user's favorites
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