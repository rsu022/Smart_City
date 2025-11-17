# api/__init__.py (Full Updated Code)

import os
from flask import Flask, send_from_directory
from api.models.waste_database import db, migrate
from api.controllers.waste_controller import garbage_bp

def create_app():
    app = Flask(__name__)
    
    # --- 1. APPLICATION CONFIGURATION ---
    
    # Define Storage Folders relative to the project root
    # BASE_DIR is api/
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Folders are created in the storage/ directory outside of the api/ package
    STORAGE_ROOT = os.path.join(BASE_DIR, '..', 'storage')
    
    app.config['UPLOAD_FOLDER'] = os.path.join(STORAGE_ROOT, 'original')
    app.config['DETECTED_FOLDER'] = os.path.join(STORAGE_ROOT, 'detected')
    
    # PostgreSQL Configuration
    # Prioritizes DATABASE_URL environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL') 

    if not DATABASE_URL:
        # FALLBACK: Use the user-provided credentials for a local PostgreSQL instance 
        # (This is only a development/testing fallback; use proper environment variables in production)
        # Ensure this is correct and the database is created in PGAdmin4
        DATABASE_URL = "postgresql://postgres:reshu890@localhost:5432/waste_detection"
        print("Warning: DATABASE_URL environment variable not set. Using hardcoded PostgreSQL fallback.")

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Create storage directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DETECTED_FOLDER'], exist_ok=True)

    # --- 2. INITIALIZE DATABASE ---
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so they are known to the DB instance for migrations
    from api.models import garbage 

    # --- 3. REGISTER BLUEPRINTS ---
    # All routes (e.g., /garbage, /garbage/<id>) will start with /api
    app.register_blueprint(garbage_bp, url_prefix='/api')

    # --- 4. STATIC FILE SERVING FOR IMAGES (REQUIRED FOR DISPLAYING IMAGES) ---
    
    # Route for original images (stored directly in UPLOAD_FOLDER)
    @app.route('/storage/original/<filename>')
    def serve_original_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Route for detected images (stored in subfolders like DETECTED_FOLDER/results/image.jpg)
    @app.route('/storage/detected/<path:filename>')
    def serve_detected_file(filename):
        # 'filename' will capture the full relative path (e.g., 'results/image.jpg')
        return send_from_directory(app.config['DETECTED_FOLDER'], filename)

    return app