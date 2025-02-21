from data_manager_interface import DataManagerInterface


class InMemoryDataManager(DataManagerInterface):
    def __init__(self):
        # Initialize in-memory storage
        self.users = {}  # Dictionary to store users (key: user_id, value: user_data)
        self.movies = {}  # Dictionary to store movies (key: movie_id, value: movie_data)

    def get_all_users(self):
        """Retrieve all users."""
        return list(self.users.values())

    def get_user_movies(self, user_id):
        """Retrieve all movies associated with a specific user."""
        user = self.users.get(user_id)
        if user:
            return [self.movies[movie_id] for movie_id in user['favorite_movies'] if movie_id in self.movies]
        return []

    def add_user(self, user_data):
        """Add a new user."""
        user_id = user_data.get('id')
        if user_id not in self.users:
            self.users[user_id] = user_data
        else:
            raise ValueError(f"User with ID {user_id} already exists.")

    def add_movie(self, movie_data):
        """Add a new movie."""
        movie_id = movie_data.get('id')
        if movie_id not in self.movies:
            self.movies[movie_id] = movie_data
        else:
            raise ValueError(f"Movie with ID {movie_id} already exists.")

    def update_user(self, user_id, updated_data):
        """Update an existing user."""
        if user_id in self.users:
            self.users[user_id].update(updated_data)
        else:
            raise ValueError(f"User with ID {user_id} does not exist.")

    def update_movie(self, movie_id, updated_data):
        """Update an existing movie."""
        if movie_id in self.movies:
            self.movies[movie_id].update(updated_data)
        else:
            raise ValueError(f"Movie with ID {movie_id} does not exist.")

    def delete_user(self, user_id):
        """Delete a user."""
        if user_id in self.users:
            del self.users[user_id]
        else:
            raise ValueError(f"User with ID {user_id} does not exist.")

    def delete_movie(self, movie_id):
        """Delete a movie."""
        if movie_id in self.movies:
            del self.movies[movie_id]
        else:
            raise ValueError(f"Movie with ID {movie_id} does not exist.")


if __name__ == "__main__":
    # Initialize the DataManager
    data_manager = InMemoryDataManager()

    # Add users
    data_manager.add_user({'id': 1, 'name': 'Alice', 'favorite_movies': []})
    data_manager.add_user({'id': 2, 'name': 'Bob', 'favorite_movies': []})

    # Add movies
    data_manager.add_movie(
        {'id': 101, 'name': 'Inception', 'director': 'Christopher Nolan', 'year': 2010, 'rating': 8.7})
    data_manager.add_movie(
        {'id': 102, 'name': 'Interstellar', 'director': 'Christopher Nolan', 'year': 2014, 'rating': 8.6})

    # Get all users
    all_users = data_manager.get_all_users()
    print("All Users:", all_users)

    # Add favorite movie for Alice
    alice = data_manager.get_all_users()[0]
    alice['favorite_movies'].append(101)
    data_manager.update_user(1, alice)

    # Get Alice's favorite movies
    alice_movies = data_manager.get_user_movies(1)
    print("Alice's Favorite Movies:", alice_movies)

    # Delete a movie
    data_manager.delete_movie(101)
    alice_movies_after_deletion = data_manager.get_user_movies(1)
    print("Alice's Favorite Movies After Deletion:", alice_movies_after_deletion)
