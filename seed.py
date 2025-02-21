# seed.py

from datamanager.sqlite_data_manager import SQLiteDataManager
from datamanager.models import db
from app import create_app  # Import the create_app function from your app.py

def seed_database(app, data_manager):
    """
    Seeds the database with sample users and movies.
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
    for movie_data in movies_data:
        try:
            data_manager.add_movie(movie_data)
            print(f"Added movie: {movie_data['name']}")
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