from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    @abstractmethod
    def get_all_users(self):
        """Retrieve all users from the data source."""
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """Retrieve all movies associated with a specific user."""
        pass

    @abstractmethod
    def add_user(self, user_data):
        """Add a new user to the data source."""
        pass

    @abstractmethod
    def add_movie(self, movie_data):
        """Add a new movie to the data source."""
        pass

    @abstractmethod
    def update_user(self, user_id, updated_data):
        """Update an existing user in the data source."""
        pass

    @abstractmethod
    def update_movie(self, movie_id, updated_data):
        """Update an existing movie in the data source."""
        pass

    @abstractmethod
    def delete_user(self, user_id):
        """Delete a user from the data source."""
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """Delete a movie from the data source."""
        pass