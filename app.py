# app.py

import os
from flask import Flask
from dotenv import load_dotenv
from datamanager.models import db
from datamanager.sqlite_data_manager import SQLiteDataManager
from routes import routes  # ✅ ONLY 'routes', not 'register_routes'

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

    # Define DB path
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'data', 'moviweb.db')
    db_uri = f"sqlite:///{db_path}"

    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Attach data manager
    app.data_manager = SQLiteDataManager(app, db_uri)

    # Register blueprint
    app.register_blueprint(routes)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
