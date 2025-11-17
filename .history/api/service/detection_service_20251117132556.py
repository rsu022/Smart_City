import os
from flask import current_app
from ultralytics import YOLO
import time
import shutil

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Models
POTHOLE_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'best.pt')
WASTE_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'waste.pt')

POTHOLE_MODEL = YOLO(POTHOLE_MODEL_PATH)
WASTE_MODEL = YOLO(WASTE_MODEL_PATH)


def detect_image_type(image):
    """
    Detects if image contains pothole or waste, saves it in appropriate folder,
    and returns detection_type and result_data dictionary.
    """
    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']

    # Ensure base folders exist
    waste_folder = os.path.join(UPLOAD_FOLDER, 'waste', 'detected')
    pothole_folder = os.path.join(UPLOAD_FOLDER, 'pothole', 'detected')
    os.makedirs(waste_folder, exist_ok=True)
    os.makedirs(pothole_folder, exist_ok=True)

    # Save original image first
    timestamp = int(time.time())
    filename = f"{timestamp}_{image.filename}"
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    # ---------- Waste Detection ----------
    waste_results = WASTE_MODEL.predict(
        source=image_path,
        save=True,
        project=os.path.join(UPLOAD_FOLDER, 'waste'),
        name='detected',
        exist_ok=True
    )

    if len(waste_results[0].boxes) > 0:
        first_class = int(waste_results[0].boxes.cls[0].item())
        CLASS_MAP = {0: 'Glass', 1: 'Metal', 2: 'Paper', 3: 'Plastic', 4: 'Residual'}
        category = CLASS_MAP.get(first_class, 'Unknown')

        # Move detected image to proper folder
        detected_image_name = os.path.basename(waste_results[0].orig_img_path)
        detected_image_path = os.path.join(waste_folder, detected_image_name)
        shutil.move(waste_results[0].orig_img_path, detected_image_path)

        return 'waste', {
            'image_name': filename,
            'detected_image_path': detected_image_path,
            'detection_status': f'{category} detected',
            'is_waste': True,
            'waste_category': category,
            'is_recyclable': True if category != 'Residual' else False,
            'is_decomposable': True if category == 'Paper' else False
        }

    # ---------- Pothole Detection ----------
    pothole_results = POTHOLE_MODEL.predict(
        source=image_path,
        save=True,
        project=os.path.join(UPLOAD_FOLDER, 'pothole'),
        name='detected',
        exist_ok=True
    )

    if len(pothole_results[0].boxes) > 0:
        detected_image_name = os.path.basename(pothole_results[0].orig_img_path)
        detected_image_path = os.path.join(pothole_folder, detected_image_name)
        shutil.move(pothole_results[0].orig_img_path, detected_image_path)

        return 'pothole', {
            'image_name': filename,
            'detected_image_path': detected_image_path,
            'status': 'Pothole detected'
        }

    # ---------- No Detection ----------
    return 'unknown', {
        'image_name': filename,
        'detected_image_path': '',
        'status': 'No detection'
    }
