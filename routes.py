from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return render_template('home.html')

@routes.route('/users')
def list_users():
    users = current_app.data_manager.get_all_users()
    return render_template('users.html', users=users)

@routes.route('/users/<int:user_id>')
def user_movies(user_id):
    user = current_app.data_manager.get_user(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('routes.list_users'))
    movies = current_app.data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user=user, movies=movies)

@routes.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        try:
            movie_data = {
                'id': request.form.get('id'),
                'name': request.form.get('name'),
                'director': request.form.get('director'),
                'year': int(request.form.get('year')),
                'rating': float(request.form.get('rating')),
                'poster': request.form.get('poster', '')
            }
            current_app.data_manager.add_movie(movie_data)
            current_app.data_manager.add_favorite_movie(user_id, movie_data['id'])
            flash("Movie added successfully!", "success")
            return redirect(url_for('routes.user_movies', user_id=user_id))
        except Exception as e:
            flash(f"Error adding movie: {e}", "error")
    return render_template('add_movie.html', user_id=user_id)

@routes.route('/users/<int:user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    movie = current_app.data_manager.get_movie_by_id(movie_id)
    if not movie:
        flash("Movie not found.", "error")
        return redirect(url_for('routes.user_movies', user_id=user_id))

    if request.method == 'POST':
        try:
            updated_data = {
                'name': request.form.get('name') or movie.name,
                'director': request.form.get('director') or movie.director,
                'year': int(request.form.get('year') or movie.year),
                'rating': float(request.form.get('rating') or movie.rating),
                'poster': request.form.get('poster') or movie.poster
            }
            current_app.data_manager.update_movie(movie_id, updated_data)
            flash("Movie updated successfully!", "success")
            return redirect(url_for('routes.user_movies', user_id=user_id))
        except Exception as e:
            flash(f"Error updating movie: {e}", "error")
    return render_template('update_movie.html', user_id=user_id, movie=movie)

@routes.route('/users/<int:user_id>/delete_movie/<movie_id>')
def delete_movie(user_id, movie_id):
    try:
        current_app.data_manager.delete_movie(movie_id)
        flash("Movie deleted.", "success")
    except Exception as e:
        flash(f"Error deleting movie: {e}", "error")
    return redirect(url_for('routes.user_movies', user_id=user_id))
