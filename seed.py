# seed.py
import os
from datamanager.sqlite_data_manager import SQLiteDataManager
from datamanager.models import db, User
import requests
from app import app, data_manager

def fetch_poster(title, api_key):
    response = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={api_key}")
    data = response.json()
    return data.get('Poster', '') if data.get('Response') == 'True' else ''

def seed_database():
    with app.app_context():
        # Clear and recreate DB
        db.drop_all()
        db.create_all()

        # Add sample users
        users = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
        for user in users:
            data_manager.add_user(user)

        # Sample movies
        omdb_api_key = os.getenv("OMDB_API_KEY")
        movies = [
            {'id': 'tt0468569', 'name': 'The Dark Knight', 'director': 'Christopher Nolan', 'year': 2008, 'rating': 9.0},
            {'id': 'tt0133093', 'name': 'The Shawshank Redemption', 'director': 'Frank Darabont', 'year': 1994, 'rating': 9.3}
        ]

        for movie in movies:
            poster = fetch_poster(movie['name'], omdb_api_key)
            movie['poster'] = poster
            data_manager.add_movie(movie)

        # Link favorites
        data_manager.add_favorite_movie(1, 'tt0468569')
        data_manager.add_favorite_movie(2, 'tt0133093')

        print("✅ Database seeded successfully!")


if __name__ == "__main__":
    seed_database()