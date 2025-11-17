import os
from flask import current_app
from ultralytics import YOLO
import time

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model paths
POTHOLE_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'best.pt')
WASTE_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'waste.pt')

# Load models
POTHOLE_MODEL = YOLO(POTHOLE_MODEL_PATH)
WASTE_MODEL = YOLO(WASTE_MODEL_PATH)


def detect_image_type(image):
    """
    Detects pothole or waste in the image and returns detection type and result dict.
    Does NOT handle saving to final folders—controller handles that.
    """
    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']

    # Save original image temporarily
    timestamp = int(time.time())
    filename = f"{timestamp}_{image.filename}"
    temp_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(temp_path)

    # ---------- Waste Detection ----------
    waste_results = WASTE_MODEL.predict(
        source=temp_path,
        save=False,  # we only want the result, saving handled in controller
    )

    if len(waste_results[0].boxes) > 0:
        first_class = int(waste_results[0].boxes.cls[0].item())
        CLASS_MAP = {0: 'Glass', 1: 'Metal', 2: 'Paper', 3: 'Plastic', 4: 'Residual'}
        category = CLASS_MAP.get(first_class, 'Unknown')

        return 'waste', {
            'image_name': filename,
            'detected_image_path': filename,  # controller will move to detected folder
            'detection_status': f'{category} detected',
            'is_waste': True,
            'waste_category': category,
            'is_recyclable': True if category != 'Residual' else False,
            'is_decomposable': True if category == 'Paper' else False
        }

    # ---------- Pothole Detection ----------
    pothole_results = POTHOLE_MODEL.predict(
        source=temp_path,
        save=False,  # controller handles saving
    )

    if len(pothole_results[0].boxes) > 0:
        return 'pothole', {
            'image_name': filename,
            'detected_image_path': filename,
            'status': 'Pothole detected'
        }

    # ---------- No Detection ----------
    return 'unknown', {
        'image_name': filename,
        'detected_image_path': '',
        'status': 'No detection'
    }
