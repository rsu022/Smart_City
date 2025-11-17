import os
from flask import current_app
from ultralytics import YOLO

# Load models
POTHOLE_MODEL = YOLO('models/best.pt')
WASTE_MODEL = YOLO('models/waste.pt')

def detect_image_type(image):
    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
    DETECTED_FOLDER = current_app.config['DETECTED_FOLDER']

    filename = image.filename
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    # Detect waste first
    waste_results = WASTE_MODEL.predict(source=image_path, save=True, project=DETECTED_FOLDER, name='waste_results', exist_ok=True)
    if len(waste_results[0].boxes) > 0:
        first_class = int(waste_results[0].boxes.cls[0].item())
        CLASS_MAP = {0:'Glass',1:'Metal',2:'Paper',3:'Plastic',4:'Residual'}
        category = CLASS_MAP.get(first_class,'Unknown')
        return 'waste', {
            'image_name': filename,
            'detected_image_path': os.path.join('waste_results', filename),
            'detection_status': f'{category} detected',
            'is_waste': True,
            'waste_category': category,
            'is_recyclable': True if category!='Residual' else False,
            'is_decomposable': True if category=='Paper' else False
        }

    # Detect pothole
    pothole_results = POTHOLE_MODEL.predict(source=image_path, save=True, project=DETECTED_FOLDER, name='pothole_results', exist_ok=True)
    if len(pothole_results[0].boxes) > 0:
        return 'pothole', {
            'image_name': filename,
            'detected_image_path': os.path.join('pothole_results', filename),
            'status': 'Pothole detected'
        }

    return 'unknown', {
        'image_name': filename,
        'detected_image_path': '',
        'status': 'No detection'
    }
