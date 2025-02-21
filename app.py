# app.py

from flask import Flask, jsonify, request, render_template, url_for, redirect, flash
from datamanager.sqllite_data_manager import SQLiteDataManager
from datamanager.models import db
import os


def create_app():
    app = Flask(__name__)

    # Configure the database
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'moviweb.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'  # For flash messages

    # Initialize the database
    db.init_app(app)

    # Create the SQLiteDataManager instance
    data_manager = SQLiteDataManager(app, app.config['SQLALCHEMY_DATABASE_URI'])

    # Attach the data manager to the app
    app.data_manager = data_manager

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()


    @app.route('/')
    def home():
        """Home page route."""
        return render_template('home.html')

    @app.route('/users')
    def users_list():
        """Display a list of all users."""
        users = app.data_manager.get_all_users()
        return render_template('users_list.html', users=users)

    @app.route('/users/<int:user_id>')
    def user_movies(user_id):
        """Display the list of movies for a specific user."""
        movies = app.data_manager.get_user_movies(user_id)
        user = next((u for u in app.data_manager.get_all_users() if u.id == user_id), None)
        if not user:
            flash("User not found!", "error")
            return redirect(url_for('users_list'))
        return render_template('user_movies.html', user=user, movies=movies)

    @app.route('/add_user', methods=['GET', 'POST'])
    def add_user():
        """Add a new user."""
        if request.method == 'POST':
            user_data = {
                'id': int(request.form['id']),
                'name': request.form['name']
            }
            try:
                app.data_manager.add_user(user_data)
                flash("User added successfully!", "success")
                return redirect(url_for('users_list'))
            except ValueError as e:
                flash(str(e), "error")
        return render_template('add_user.html')

    @app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
    def add_movie(user_id):
        """Add a new movie to a user's favorites."""
        if request.method == 'POST':
            movie_data = {
                'id': int(request.form['id']),
                'name': request.form['name'],
                'director': request.form['director'],
                'year': int(request.form['year']),
                'rating': float(request.form['rating'])
            }
            try:
                app.data_manager.add_movie(movie_data)
                flash("Movie added successfully!", "success")
                return redirect(url_for('user_movies', user_id=user_id))
            except ValueError as e:
                flash(str(e), "error")
        return render_template('add_movie.html', user_id=user_id)

    @app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
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
                app.data_manager.update_movie(movie_id, updated_data)
                flash("Movie updated successfully!", "success")
                return redirect(url_for('user_movies', user_id=user_id))
            except ValueError as e:
                flash(str(e), "error")
        return render_template('update_movie.html', user_id=user_id, movie_id=movie_id)

    @app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET', 'POST'])
    def delete_movie(user_id, movie_id):
        """Delete a movie from a user's favorites."""
        try:
            app.data_manager.delete_movie(movie_id)
            flash("Movie deleted successfully!", "success")
        except ValueError as e:
            flash(str(e), "error")
        return redirect(url_for('user_movies', user_id=user_id))

    @app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
    def delete_user(user_id):
        """Delete a user."""
        try:
            app.data_manager.delete_user(user_id)
            flash("User deleted successfully!", "success")
        except ValueError as e:
            flash(str(e), "error")
        return redirect(url_for('users_list'))



    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)