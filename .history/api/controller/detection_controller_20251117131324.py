from flask import Blueprint, request, jsonify
from database import db
from api.models.detection_model import Pothole, Waste
from api.service.detection_service import detect_image_type

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

    detection_type, result_data = detect_image_type(image)

    if detection_type == 'pothole':
        record = Pothole(
            image_name=result_data['image_name'],
            detected_image_path=result_data['detected_image_path'],
            location=location,
            latitude=float(lat),
            longitude=float(lon),
            status=result_data['status']
        )
    elif detection_type == 'waste':
        record = Waste(
            image_name=result_data['image_name'],
            detected_image_path=result_data['detected_image_path'],
            location=location,
            latitude=float(lat),
            longitude=float(lon),
            detection_status=result_data['detection_status'],
            is_waste=result_data['is_waste'],
            waste_category=result_data['waste_category'],
            is_recyclable=result_data['is_recyclable'],
            is_decomposable=result_data['is_decomposable']
        )
    else:
        return jsonify({'message': 'No detection found'}), 200

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
