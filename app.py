# app.py

from flask import Flask
from datamanager import SQLiteDataManager, db

def create_app(db_uri):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database
    db.init_app(app)

    # Create the SQLiteDataManager instance
    data_manager = SQLiteDataManager(app, db_uri)

    # Attach the data manager to the app
    app.data_manager = data_manager

    return app

if __name__ == '__main__':
    app = create_app('sqlite:///moviweb.db')
    app.run(debug=True)