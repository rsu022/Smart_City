from flask import Blueprint, request, jsonify, current_app
# FIX: Correct imports
from api.models.garbage import Detection
from api.models.waste_database import db 
from api.services.waste_service import processed_detection 
import os
from datetime import datetime

garbage_bp = Blueprint("garbage_bp", __name__)

# GET = Fetch all garbage records
@garbage_bp.route('/garbage', methods=['GET'])
def get_all_garbage():
    garbage_records = Detection.query.all() # FIX: Use Detection
    return jsonify([g.to_dict() for g in garbage_records]), 200


# GET = Fetch garbage record by ID
@garbage_bp.route('/garbage/<int:id>', methods=['GET'])
def get_garbage_by_id(id):
    record = Detection.query.get(id) # FIX: Use Detection
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify(record.to_dict()), 200


# POST = Upload image + geolocation data (REFACTORED)
@garbage_bp.route('/garbage', methods=['POST'])
def upload_garbage_image():
    # Note: Flask will handle the file storage on the image object until it's read/saved
    image = request.files.get('image')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    location = request.form.get('location')

    if not image or not latitude or not longitude or not location:
        return jsonify({'error': 'Missing required fields: image, latitude, longitude, or location'}), 400

    try:
        # Calls the service which handles file saving, YOLO detection, and DB commit
        record_data = processed_detection(image, latitude, longitude, location)
    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Error during detection service call: {e}")
        return jsonify({'error': f'Internal server error during processing: {e}'}), 500

    return jsonify({
        'message': 'Garbage image uploaded, processed, and data saved successfully',
        'data': record_data
    }), 201


# PUT = Update garbage record info
@garbage_bp.route('/garbage/<int:id>', methods=['PUT'])
def update_garbage_record(id):
    record = Detection.query.get(id) # FIX: Use Detection
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    # FIX: Use correct field name 'garbage_location'
    record.garbage_location = request.form.get('location', record.garbage_location) 
    record.latitude = request.form.get('latitude', record.latitude)
    record.longitude = request.form.get('longitude', record.longitude)
    record.detection_status = request.form.get('status', record.detection_status)
    # Note: You may want to prevent updating classification fields via PUT

    db.session.commit()

    return jsonify({
        'message': 'Garbage record updated successfully',
        'data': record.to_dict()
    }), 200


# Helper to delete files (Updated to use config for correct path)
def delete_files(record):
    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
    DETECTED_FOLDER = current_app.config['DETECTED_FOLDER']
    
    # Delete original image
    original_path = os.path.join(UPLOAD_FOLDER, record.image_name)
    if os.path.exists(original_path):
        try:
            os.remove(original_path)
        except Exception as e:
            print(f"Error deleting original file {original_path}: {e}")

    # Delete detected image (path is relative to DETECTED_FOLDER)
    detected_path = os.path.join(DETECTED_FOLDER, record.detected_image_path)
    if os.path.exists(detected_path):
        try:
            os.remove(detected_path)
        except Exception as e:
            print(f"Error deleting detected file {detected_path}: {e}")


# DELETE = Remove all records
@garbage_bp.route('/garbage', methods=['DELETE'])
def delete_all_garbage():
    records = Detection.query.all() # FIX: Use Detection
    if not records:
        return jsonify({'error': 'No records found to delete'}), 404

    count = 0
    for record in records:
        delete_files(record)
        db.session.delete(record)
        count += 1

    db.session.commit()
    return jsonify({'message': f'All {count} garbage records deleted successfully'}), 200


# DELETE = Remove by ID
@garbage_bp.route('/garbage/<int:id>', methods=['DELETE'])
def delete_garbage_by_id(id):
    record = Detection.query.get(id) # FIX: Use Detection
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    delete_files(record)
    db.session.delete(record)
    db.session.commit()

    return jsonify({'message': 'Garbage record deleted successfully'}), 200