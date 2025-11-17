import os
import time
from flask import current_app
from ultralytics import YOLO

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Models
POTHOLE_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'best.pt')
WASTE_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'waste.pt')

# Load models
POTHOLE_MODEL = YOLO(POTHOLE_MODEL_PATH)
WASTE_MODEL = YOLO(WASTE_MODEL_PATH)


def detect_image_type(image):
    """
    Detects if the image contains pothole or waste, returns detection_type and result dict.
    Controller handles saving to final folders.
    """
    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']

    # Ensure base upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Save original uploaded image temporarily
    timestamp = int(time.time())
    filename = f"{timestamp}_{image.filename}"
    temp_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(temp_path)

    # ---------- Waste Detection ----------
    waste_results = WASTE_MODEL.predict(
        source=temp_path,
        save=False
    )

    if len(waste_results[0].boxes) > 0:
        first_class = int(waste_results[0].boxes.cls[0].item())
        CLASS_MAP = {0: 'Glass', 1: 'Metal', 2: 'Paper', 3: 'Plastic', 4: 'Residual'}
        category = CLASS_MAP.get(first_class, 'Unknown')

        return 'waste', {
            'image_name': filename,
            'detected_image_path': filename,  # controller moves to detected folder
            'detection_status': f'{category} detected',
            'is_waste': True,
            'waste_category': category,
            'is_recyclable': category != 'Residual',
            'is_decomposable': category == 'Paper'
        }

    # ---------- Pothole Detection ----------
    pothole_results = POTHOLE_MODEL.predict(
        source=temp_path,
        save=False
    )

    if len(pothole_results[0].boxes) > 0:
        return 'pothole', {
            'image_name': filename,
            'detected_image_path': filename,  # controller moves to detected folder
            'status': 'Pothole detected'
        }

    # ---------- No Detection ----------
    return 'unknown', {
        'image_name': filename,
        'detected_image_path': '',
        'status': 'No detection'
    }
