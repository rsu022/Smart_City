#to handle all HTTP requests
#defines alll API routes
from flask import Blueprint, request, jsonify,current_app, send_from_directory
from service.detection_service import processed_detection
from models.detection_model import Detection
from database import db
import os
from sqlalchemy import delete

detection_bp = Blueprint("detection_bp", __name__)
# GET= to fetch all detections at once 
@detection_bp.route('/detect', methods=['GET'])
def get_all_detections():
    detections = Detection.query.all()
    return jsonify([d.to_dict() for d in detections]), 200


# GET =by ID
@detection_bp.route('/detect/<int:id>', methods=['GET'])
def get_detection_by_id(id):
    detection = Detection.query.get(id)
    if not detection:
        return jsonify({'error': 'Detection not found'}), 404
    return jsonify(detection.to_dict()), 200

# POST=upload the image
@detection_bp.route('/detect', methods=['POST'])
def detect_pothole():
    image = request.files.get('image')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    location = request.form.get('location')

    if not image or not lat or not lon or not location:
        return jsonify({'error': 'Missing required fields...'}), 400

    results = processed_detection(image, lat, lon, location)
    return jsonify({"message": "Detection saved", "data": results}), 201



# PUT= Update detection status or info
@detection_bp.route('/detect/<int:id>', methods=['PUT'])
def update_detection(id):
    detection = Detection.query.get(id)
    if not detection:
        return jsonify({'error': 'Detection not found'}), 404
    
    detection.location = request.form.get('location', detection.location)
    #to update the status
    detection.status = request.form.get('status', detection.status)
    
    detection.latitude = request.form.get('latitude', detection.latitude)
    detection.longitude = request.form.get('longitude', detection.longitude)
    db.session.commit()
    
    # Return the updated detection object to confirm the status change immediately
    return jsonify({'message': 'Detection status updated successfully', 'data': detection.to_dict()}), 200



#DELETE Request

#function to delete the saved files
def delete_files(detection):
    DETECTED_FOLDER = current_app.config['DETECTED_FOLDER']
    # to delete detected (processed) image (from the 'detected_potholes/results' folder)
    detected_relative_path = detection.detected_image_path
    if detected_relative_path:
        detected_full_path = os.path.join(DETECTED_FOLDER, detected_relative_path)
        try:
            if os.path.exists(detected_full_path):
                os.remove(detected_full_path)
        except Exception as e:
            print(f"Error deleting detected image file {detected_full_path}: {e}")


# DELETE= remove all dtection and files
@detection_bp.route('/detect', methods=['DELETE'])
def delete_all_detections():
    #fetcing all detections to gettheir file paths
    detections = Detection.query.all()
    if not detections:
        return jsonify({'error': 'No detections found to delete!'}), 404
    deleted_count = 0

    #Iterate, delete files and stage database deletion for each record inthe db
    for detection in detections:
        delete_files(detection)
        db.session.delete(detection)
        deleted_count += 1
    try:
        db.session.commit()
        return jsonify({'message': f'All {deleted_count} detection files are deleted successfully'}), 200
    except Exception as e:
        # if in case of database error
        db.session.rollback()
        print(f"Error during database deletion: {e}")
        return jsonify({'error': 'Failed to delete records from the database!'}), 500


# DELETE= by id (remove simgle file)
@detection_bp.route('/detect/<int:id>', methods=['DELETE'])
def delete_detection_by_id(id):
    detection = Detection.query.get(id) #ORM use vako
    if not detection:
        return jsonify({'error': 'Detection not found'}), 404
    #to deelete associated files first
    delete_files(detection)

    # to delete the database record
    db.session.delete(detection)
    db.session.commit()
    
    return jsonify({'message': 'Detection file  deleted successfully'}), 200