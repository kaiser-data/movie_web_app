from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy object
db = SQLAlchemy()

class User(db.Model):
    """
    Represents a user in the database.

    Attributes:
        id (int): The unique identifier for the user (primary key).
        name (str): The name of the user (cannot be null).
        favorite_movies (relationship): A many-to-many relationship with the Movie model,
            representing the user's favorite movies.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    favorite_movies = db.relationship('Movie', secondary='user_movie', backref='users', lazy=True)

class Movie(db.Model):
    """
    Represents a movie in the database.

    Attributes:
        id (str): The unique identifier for the movie (primary key). Typically an external ID like IMDB ID.
        name (str): The name of the movie (cannot be null).
        director (str): The name of the director of the movie (cannot be null).
        year (int): The release year of the movie (cannot be null).
        rating (float): The rating of the movie (cannot be null).
    """
    __tablename__ = 'movies'
    id = db.Column(db.String(50), primary_key=True)  # Change id to String for external IDs
    name = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)

# Secondary table for many-to-many relationship between users and movies
user_movie = db.Table(
    'user_movie',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('movie_id', db.String(50), db.ForeignKey('movies.id'), primary_key=True)  # Update movie_id to String
)