from flask import Flask
from flask_cors import CORS
from database import db, migrate
from controllers.detection_controller import detection_bp
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    # PostgreSQL Config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:yourpassword@localhost:5432/detection_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Upload / Detected folders
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
    app.config['DETECTED_FOLDER'] = os.path.join(BASE_DIR, 'detected')

    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'waste'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'potholes'), exist_ok=True)
    os.makedirs(os.path.join(app.config['DETECTED_FOLDER'], 'waste'), exist_ok=True)
    os.makedirs(os.path.join(app.config['DETECTED_FOLDER'], 'potholes'), exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprint
    app.register_blueprint(detection_bp, url_prefix='/api/detections')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
