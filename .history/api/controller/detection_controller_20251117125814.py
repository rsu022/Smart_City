from flask import Blueprint, request, jsonify
from database import db
from api.models.detection_model import Pothole, Waste
from api.services.detection_service import detect_image_type

detection_bp = Blueprint('detection_bp', __name__)

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
        return jsonify({'message':'No detection found'}), 200

    db.session.add(record)
    db.session.commit()

    return jsonify({
        'message': f'{detection_type.capitalize()} detected successfully',
        'data': record.to_dict()
    }), 201
