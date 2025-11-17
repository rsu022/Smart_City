#main file that starts the Flask server and integrates everything

from flask import Flask
from controller.detection_controller import detection_bp
import os
from database import db
from models.detection_model import Detection 
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)

    # Database connection
    #database connection(using %40 for @ because my username is @user123 and  @ cant be usedfor username  at this moment )
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:%40user123@localhost/detections'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Upload and detection folders
    MAIN_FOLDER = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(MAIN_FOLDER, 'uploads')
    app.config['DETECTED_FOLDER'] = os.path.join(MAIN_FOLDER, 'detected_potholes')
    app.config['PROCESSED_IMAGE'] = "results" #to save all the results(processed image after i intgerate post request)inside the same folder

    # Initializing SQLAlchemy with Flask application

    # Initialize SQLAlchemy and Flask-Migrate
    db.init_app(app)
    migrate = Migrate(app, db)

    # to register Blueprint
    app.register_blueprint(detection_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()

    # to check whether the folders exits
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DETECTED_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['DETECTED_FOLDER'], app.config['PROCESSED_IMAGE']), exist_ok=True)

    app.run(debug=True)


    # #to intearct with sqlalchemy
    # with app.app_context():
    #     # to create all database tables based on models(i.e detection)
    #     # db.create_all()
    #     # print("Database tables created succesfully.")
    
    
    # Note: instead of db.create_all using Flask-Migrate fro database schema 