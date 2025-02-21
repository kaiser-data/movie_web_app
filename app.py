# app.py

from flask import Flask, jsonify, request, render_template
from datamanager.sqllite_data_manager import SQLiteDataManager
from datamanager.models import db
import os

def create_app():
    # Initialize the Flask application
    app = Flask(__name__)

    # Construct the database URI to point to the 'data' folder
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'moviweb.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database
    db.init_app(app)

    # Create the SQLiteDataManager instance
    data_manager = SQLiteDataManager(app, app.config['SQLALCHEMY_DATABASE_URI'])

    # Attach the data manager to the app
    app.data_manager = data_manager

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # Define routes

    @app.route('/')
    def home():
        """Home page route."""
        return "Welcome to MovieWeb App!"

    @app.route('/users', methods=['GET'])
    def get_all_users():
        """Get a list of all users."""
        users = app.data_manager.get_all_users()
        return jsonify([user.as_dict() for user in users])

    @app.route('/users/<int:user_id>/movies', methods=['GET'])
    def get_user_movies(user_id):
        """Get movies associated with a specific user."""
        movies = app.data_manager.get_user_movies(user_id)
        return jsonify([movie.as_dict() for movie in movies])

    @app.route('/users', methods=['POST'])
    def add_user():
        """Add a new user."""
        user_data = request.json
        try:
            app.data_manager.add_user(user_data)
            return jsonify({"message": "User added successfully."}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/movies', methods=['POST'])
    def add_movie():
        """Add a new movie."""
        movie_data = request.json
        try:
            app.data_manager.add_movie(movie_data)
            return jsonify({"message": "Movie added successfully."}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    def delete_movie(movie_id):
        """Delete a movie."""
        try:
            app.data_manager.delete_movie(movie_id)
            return jsonify({"message": "Movie deleted successfully."}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    @app.route('/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        """Delete a user."""
        try:
            app.data_manager.delete_user(user_id)
            return jsonify({"message": "User deleted successfully."}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    @app.route('/movies/<int:movie_id>', methods=['PUT'])
    def update_movie(movie_id):
        """Update a movie."""
        updated_data = request.json
        try:
            app.data_manager.update_movie(movie_id, updated_data)
            return jsonify({"message": "Movie updated successfully."}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    @app.route('/users/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        """Update a user."""
        updated_data = request.json
        try:
            app.data_manager.update_user(user_id, updated_data)
            return jsonify({"message": "User updated successfully."}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)