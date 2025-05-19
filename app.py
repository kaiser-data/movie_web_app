# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import os
from datamanager.models import db, User
from datamanager.sqlite_data_manager import SQLiteDataManager
from omdb_service import fetch_movie_data, extract_movie_data
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Secret key for session management / flash messages
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

# Setup database URI
base_dir = os.path.abspath(os.path.dirname(__file__))
# SQLite database path
db_path = os.path.join(base_dir, 'data', 'movies.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database object
db.init_app(app)

# Create tables inside app context
with app.app_context():
    db.create_all()

# Initialize data manager with the actual URI
# Pass the URI string so the manager can reconfigure SQLAlchemy
data_manager = SQLiteDataManager(app, app.config['SQLALCHEMY_DATABASE_URI'])

# Inject current year into templates
@app.context_processor
def inject_year():
    import datetime
    return dict(current_year=datetime.datetime.now().year)


@app.route("/")
def home():
    """Home page"""
    return render_template('home.html')


@app.route('/users')
def list_users():
    """List all users"""
    try:
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except Exception as e:
        flash(f"Error loading users: {e}", "error")
        return redirect(url_for('home'))


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """Show movies for a specific user"""
    user = data_manager.get_user(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('list_users'))
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user=user, movies=movies)


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    """Add a new user with auto-incremented ID"""
    if request.method == "POST":
        name = request.form.get("username")
        if not name or name.strip() == "":
            flash("Name cannot be empty!", "error")
            return redirect(url_for("add_user"))

        try:
            max_id = db.session.query(db.func.max(User.id)).scalar() or 0
            new_id = max_id + 1
            new_user = User(id=new_id, name=name)
            db.session.add(new_user)
            db.session.commit()
            flash("✅ User added successfully!", "success")
            return redirect(url_for("list_users"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error adding user: {e}", "error")
            return redirect(url_for("add_user"))

    return render_template("add_user.html")


@app.route("/users/<int:user_id>/add_movie", methods=["GET", "POST"])
def add_movie(user_id):
    """Add a movie to a user's list via OMDb."""
    user = data_manager.get_user(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("list_users"))

    if request.method == "POST":
        title = request.form.get("title")
        if not title:
            flash("Movie title is required!", "error")
            return redirect(url_for("add_movie", user_id=user_id))

        # 1) Fetch from OMDb
        raw_data = fetch_movie_data(title)
        if not raw_data or "Error" in raw_data:
            flash(raw_data.get("Error", "Movie not found."), "error")
            return render_template("add_movie.html", user=user)

        # 2) Extract and normalize
        movie_data = extract_movie_data(raw_data)

        # 3) Try to insert into DB (True = new insert, False = already exists)
        is_new = data_manager.add_movie(movie_data)

        # 4) Link to this user's favorites (if not already linked)
        try:
            data_manager.add_favorite_movie(user_id, movie_data["id"])
            if is_new:
                flash("✅ Movie added and linked to your list!", "success")
            else:
                flash("ℹ️ Movie was already in the database—linked to your list.", "info")
        except ValueError:
            flash("⚠️ Movie is already in your favorites.", "error")

        return redirect(url_for("user_movies", user_id=user_id))

    # GET request → render search form
    return render_template("add_movie.html", user=user)



@app.route('/users/<int:user_id>/update_movie/<string:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update an existing movie"""
    user = data_manager.get_user(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('list_users'))

    movie = data_manager.get_movie(movie_id)
    if not movie or movie not in user.favorite_movies:
        flash("Movie not found.", "error")
        return redirect(url_for('user_movies', user_id=user_id))

    if request.method == 'POST':
        try:
            updated_data = {
                'name':     request.form.get('name')     or movie.name,
                'director': request.form.get('director') or movie.director,
                'genre':    request.form.get('genre')    or movie.genre,
                'year':     int(request.form.get('year') or movie.year),
                'rating':   float(request.form.get('rating') or movie.rating),
                'poster':   request.form.get('poster')   or movie.poster
            }
            data_manager.update_movie(movie_id, updated_data)
            flash("✅ Movie updated successfully!", "success")
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            flash(f"❌ Error updating movie: {e}", "error")
            return redirect(url_for('user_movies', user_id=user_id))

    # Render with user_id context so template back-link works
    return render_template(
        'update_movie.html',
        user=user,
        movie=movie,
        user_id=user_id
    )


@app.route('/users/<int:user_id>/delete_movie/<string:movie_id>')
def delete_movie(user_id, movie_id):
    """Delete a movie from user's favorites"""
    try:
        data_manager.delete_movie(movie_id)
        flash("🗑️ Movie deleted successfully!", "success")
    except Exception as e:
        flash(f"⚠️ Error deleting movie: {e}", "error")
    return redirect(url_for('user_movies', user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 handler"""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Custom 500 handler"""
    return render_template("500.html"), 500


if __name__ == "__main__":
    print("✅ Running Flask App... on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
