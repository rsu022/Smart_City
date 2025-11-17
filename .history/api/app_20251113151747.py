import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from database import db  # Shared DB instance

# ---------------- Blueprints ----------------
from controller.detection_controller import detection_bp
from api.controller.waste_controller import garbage_bp

# ---------------- App Factory ----------------
def create_app():
    app = Flask(__name__)
    CORS(app)

    # ---------------- Database Config ----------------
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:%40user123@localhost/detections'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/detections'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ---------------- Upload / Detection Folders ----------------
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Waste uploads
    app.config['WASTE_UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads', 'waste')
    app.config['WASTE_DETECTED_FOLDER'] = os.path.join(BASE_DIR, 'detected', 'waste')

    # Pothole uploads
    app.config['POTHOLE_UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads', 'potholes')
    app.config['POTHOLE_DETECTED_FOLDER'] = os.path.join(BASE_DIR, 'detected', 'potholes')
    app.config['PROCESSED_IMAGE'] = "results"  # for processed images

    # Create folders if not exist
    os.makedirs(app.config['WASTE_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['WASTE_DETECTED_FOLDER'], exist_ok=True)
    os.makedirs(app.config['POTHOLE_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['POTHOLE_DETECTED_FOLDER'], app.config['PROCESSED_IMAGE']), exist_ok=True)

    # ---------------- Initialize DB ----------------
    db.init_app(app)
    migrate = Migrate(app, db)

    # ---------------- Register Blueprints ----------------
    app.register_blueprint(garbage_bp, url_prefix='/api/garbage')
    app.register_blueprint(detection_bp, url_prefix='/api/detection')

    # ---------------- Default Route ----------------
    @app.route('/')
    def home():
        return {
            "message": "Flask API running 🚀",
            "endpoints": {
                "Waste API": {
                    "GET all": "/api/garbage",
                    "GET by id": "/api/garbage/<id>",
                    "POST": "/api/garbage",
                    "PUT": "/api/garbage/<id>",
                    "DELETE all": "/api/garbage",
                    "DELETE by id": "/api/garbage/<id>"
                },
                "Pothole API": {
                    "GET all": "/api/detection",
                    "GET by id": "/api/detection/<id>",
                    "POST": "/api/detection",
                }
            }
        }

    return app


# ---------------- Run Server ----------------
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
