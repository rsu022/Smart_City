import os
from datetime import datetime
from flask import current_app
from api.models.garbage import Detection
from api.models.waste_database import db 
from ultralytics import YOLO

# Define the base directory (where waste_service.py is located: api/services)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# FIX: Corrected Model Path
MODEL_PATH = os.path.
oin(BASE_DIR, '..', 'models', 'waste.pt')
model = YOLO(MODEL_PATH)

# FIX: CLASSIFICATION_MAP based on your data.yaml names order: [glass, metal, paper, plastic, residual]
CLASSIFICATION_MAP = {
    0: {'category': 'Glass', 'recyclable': True, 'decomposable': False},
    1: {'category': 'Metal', 'recyclable': True, 'decomposable': False},
    2: {'category': 'Paper', 'recyclable': True, 'decomposable': True},
    3: {'category': 'Plastic', 'recyclable': True, 'decomposable': False},
    4: {'category': 'Residual', 'recyclable': False, 'decomposable': False},
}


def processed_detection(image, latitude, longitude, location):
    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
    DETECTED_FOLDER = current_app.config['DETECTED_FOLDER']

    # Saving uploaded image
    filename = image.filename
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    # Running YOLOv8 detection
    results = model.predict(
        source=image_path,
        save=True, 
        project=DETECTED_FOLDER, 
        name="results", 
        conf=0.4, 
        exist_ok=True
        )
    
    # Path to the detected image
    yolo_run_name = os.path.basename(results[0].save_dir)
    detected_path = os.path.join(yolo_run_name, filename)

    # NEW CLASSIFICATION LOGIC
    is_waste = False
    waste_category = "None"
    is_recyclable = False
    is_decomposable = False
    detection_status = "No Garbage detected"

    if len(results[0].boxes) > 0:
        first_class_id = int(results[0].boxes.cls[0].item())
        
        if first_class_id in CLASSIFICATION_MAP:
            classification = CLASSIFICATION_MAP[first_class_id]
            
            is_waste = True
            waste_category = classification['category']
            is_recyclable = classification['recyclable']
            is_decomposable = classification['decomposable']
            
            # Use the model's internal name for the status
            predicted_name = model.names[first_class_id]
            detection_status = f"{predicted_name.capitalize()} detected (Model ID: {first_class_id})"


    # Saving record in DB
    detection = Detection(
        image_name=filename,
        detected_image_path=detected_path,
        garbage_location=location,
        latitude=float(latitude),
        longitude=float(longitude),
        timestamp=datetime.utcnow(),
        detection_status=detection_status,
        is_waste=is_waste,
        waste_category=waste_category,
        is_recyclable=is_recyclable,
        is_decomposable=is_decomposable
    )

    db.session.add(detection)
    db.session.commit()

    return detection.to_dict()