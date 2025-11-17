import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from database import db
from api.models.detection_model import Pothole, Waste
from api.service.detection_service import detect_image_type

detection_bp = Blueprint('detection_bp', __name__, url_prefix='/detections')

# Base upload folder
UPLOAD_FOLDER = "uploads"

# ---------------- POST: Detect and save ----------------
@detection_bp.route('/', methods=['POST'])
def detect():
    image = request.files.get('image')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    location = request.form.get('location')

    if not image or not lat or not lon or not location:
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate latitude/longitude
    try:
        latitude = float(lat)
        longitude = float(lon)
    except ValueError:
        return jsonify({'error': 'Latitude and longitude must be valid decimal numbers'}), 400

    detection_type, result_data = detect_image_type(image)

    if detection_type not in ['pothole', 'waste']:
        return jsonify({'message': 'No detection found'}), 200

    # Create folders if not exist
    original_folder = os.path.join(UPLOAD_FOLDER, detection_type, "original")
    detected_folder = os.path.join(UPLOAD_FOLDER, detection_type, "detected")
    os.makedirs(original_folder, exist_ok=True)
    os.makedirs(detected_folder, exist_ok=True)

    # Save original image
    original_filename = secure_filename(result_data['image_name'])
    original_path = os.path.join(original_folder, original_filename)
    image.save(original_path)

    # Save detected image
    detected_filename = secure_filename(result_data['detected_image_path'].split('/')[-1])
    detected_path = os.path.join(detected_folder, detected_filename)
    if os.path.exists(result_data['detected_image_path']):
        os.rename(result_data['detected_image_path'], detected_path)
    result_data['detected_image_path'] = detected_path  # update path in DB

    # Save to DB
    if detection_type == 'pothole':
        record = Pothole(
            image_name=original_filename,
            detected_image_path=detected_path,
            location=location,
            latitude=latitude,
            longitude=longitude,
            status=result_data['status']
        )
    else:  # waste
        record = Waste(
            image_name=original_filename,
            detected_image_path=detected_path,
            location=location,
            latitude=latitude,
            longitude=longitude,
            detection_status=result_data['detection_status'],
            is_waste=result_data['is_waste'],
            waste_category=result_data['waste_category'],
            is_recyclable=result_data['is_recyclable'],
            is_decomposable=result_data['is_decomposable']
        )

    db.session.add(record)
    db.session.commit()

    return jsonify({
        'message': f'{detection_type.capitalize()} detected successfully',
        'data': record.to_dict()
    }), 201


# ---------------- GET: Retrieve all detections ----------------
@detection_bp.route('/', methods=['GET'])
def get_all_detections():
    potholes = [p.to_dict() for p in Pothole.query.all()]
    wastes = [w.to_dict() for w in Waste.query.all()]
    return jsonify({'potholes': potholes, 'wastes': wastes}), 200


# ---------------- GET: Retrieve single detection by ID ----------------
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
    return jsonify({'message': f'{detection_type.capitalize()} deleted successfully'}), 200
