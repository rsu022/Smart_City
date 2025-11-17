import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from database import db
from api.models.detection_model import Pothole, Waste
from api.service.detection_service import detect_image_type

# Base Blueprint
detection_bp = Blueprint('detection_bp', __name__, url_prefix='/detections')


# ---------------- POST: Detect and save ----------------
@detection_bp.route('/', methods=['POST'])
def detect():
    image = request.files.get('image')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    location = request.form.get('location')

    if not image or not lat or not lon or not location:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        latitude = float(lat)
        longitude = float(lon)
    except ValueError:
        return jsonify({'error': 'Latitude and Longitude must be valid numbers'}), 400

    # Call service to detect and save image temporarily
    detection_type, result_data = detect_image_type(image)

    if not detection_type:
        return jsonify({'message': 'No pothole or waste detected in the image'}), 200

    # Get the UPLOAD_FOLDER from the application configuration
    UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER')
    if not UPLOAD_FOLDER:
        return jsonify({'error': 'UPLOAD_FOLDER is not configured in Flask app'}), 500

    # Filenames from service (these are temporary names in UPLOAD_FOLDER)
    temp_original_filename = result_data['image_name']
    temp_detected_filename = result_data['detected_image_path']

    # --- Create directories and paths ---
    original_folder = os.path.join(UPLOAD_FOLDER, detection_type, "original")
    detected_folder = os.path.join(UPLOAD_FOLDER, detection_type, "detected")
    os.makedirs(original_folder, exist_ok=True)
    os.makedirs(detected_folder, exist_ok=True)

    # 1. Move the original uploaded image from temp location to final 'original' folder
    temp_original_path = os.path.join(UPLOAD_FOLDER, temp_original_filename)
    final_original_path = os.path.join(original_folder, temp_original_filename)
    
    if os.path.exists(temp_original_path):
        # Move temporary original file to final original folder
        os.rename(temp_original_path, final_original_path)
    else:
        # Critical failure: file was not saved by service
        return jsonify({'error': 'Uploaded image file was not found after detection'}), 500
    
    
    final_detected_image_path_db = None
    
    # 2. Move the detected (annotated) image from temp location to final 'detected' folder
    if temp_detected_filename:
        temp_detected_path = os.path.join(UPLOAD_FOLDER, temp_detected_filename)
        final_detected_path = os.path.join(detected_folder, temp_detected_filename)

        if os.path.exists(temp_detected_path):
            # Move temporary detected file to final detected folder
            os.rename(temp_detected_path, final_detected_path)
            # Save the full path to the database
            final_detected_image_path_db = final_detected_path 
            
    # --- Create DB record ---
    if detection_type == 'pothole':
        record = Pothole(
            image_name=temp_original_filename,
            detected_image_path=final_detected_image_path_db,
            location=location,
            latitude=latitude,
            longitude=longitude,
            status=result_data['status']
        )
    elif detection_type == 'waste':
        record = Waste(
            image_name=temp_original_filename,
            detected_image_path=final_detected_image_path_db,
            location=location,
            latitude=latitude,
            longitude=longitude,
            detection_status=result_data['detection_status'],
            is_waste=result_data['is_waste'],
            waste_category=result_data['waste_category'],
            is_recyclable=result_data['is_recyclable'],
            is_decomposable=result_data['is_decomposable']
        )
    else:
        return jsonify({'error': 'Invalid detection type from service'}), 500

    db.session.add(record)
    db.session.commit()
    return jsonify({'message': f'{detection_type.capitalize()} detected and saved', 'data': record.to_dict()}), 201

# ---------------- GET: Retrieve all detections ----------------
@detection_bp.route('/<string:detection_type>', methods=['GET'])
def get_detections(detection_type):
    if detection_type == 'pothole':
        records = Pothole.query.all()
    elif detection_type == 'waste':
        records = Waste.query.all()
    else:
        return jsonify({'error': 'Invalid detection type'}), 400

    return jsonify([record.to_dict() for record in records]), 200

# ---------------- GET: Retrieve single detection ----------------
@detection_bp.route('/<string:detection_type>/<int:id>', methods=['GET'])
def get_detection(detection_type, id):
    if detection_type == 'pothole':
        record = Pothole.query.get_or_404(id)
    elif detection_type == 'waste':
        record = Waste.query.get_or_404(id)
    else:
        return jsonify({'error': 'Invalid detection type'}), 400

    return jsonify(record.to_dict()), 200

# ---------------- PUT: Update detection ----------------
@detection_bp.route('/<string:detection_type>/<int:id>', methods=['PUT'])
def update_detection(detection_type, id):
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if detection_type == 'pothole':
        record = Pothole.query.get_or_404(id)
        record.status = data.get('status', record.status)
        record.location = data.get('location', record.location)
        record.latitude = data.get('latitude', record.latitude)
        record.longitude = data.get('longitude', record.longitude)
    elif detection_type == 'waste':
        record = Waste.query.get_or_404(id)
        record.detection_status = data.get('detection_status', record.detection_status)
        record.is_waste = data.get('is_waste', record.is_waste)
        record.waste_category = data.get('waste_category', record.waste_category)
        record.is_recyclable = data.get('is_recyclable', record.is_recyclable)
        record.is_decomposable = data.get('is_decomposable', record.is_decomposable)
        record.location = data.get('location', record.location)
        record.latitude = data.get('latitude', record.latitude)
        record.longitude = data.get('longitude', record.longitude)
    else:
        return jsonify({'error': 'Invalid detection type'}), 400

    db.session.commit()
    return jsonify({'message': f'{detection_type.capitalize()} updated', 'data': record.to_dict()}), 200


# ---------------- DELETE: Remove detection ----------------
@detection_bp.route('/<string:detection_type>/<int:id>', methods=['DELETE'])
def delete_detection(detection_type, id):
    if detection_type == 'pothole':
        record = Pothole.query.get_or_404(id)
    elif detection_type == 'waste':
        record = Waste.query.get_or_404(id)
    else:
        return jsonify({'error': 'Invalid detection type'}), 400

    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': f'{detection_type.capitalize()} with ID {id} deleted'}), 200