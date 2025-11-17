import os
import time
from flask import current_app
from ultralytics import YOLO

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Models
# NOTE: Ensure these paths are correct relative to your Flask app structure
POTHOLE_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'best.pt')
WASTE_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'waste.pt')

# Load models
# NOTE: Error handling added for model loading
try:
    POTHOLE_MODEL = YOLO(POTHOLE_MODEL_PATH)
    WASTE_MODEL = YOLO(WASTE_MODEL_PATH)
except Exception as e:
    # Handle the error appropriately, perhaps log it or raise
    print(f"Error loading models: {e}. Check your model paths.")
    POTHOLE_MODEL = None
    WASTE_MODEL = None

def detect_image_type(image):
    """
    Detects if the image contains pothole or waste.
    Saves the original and detected image temporarily to UPLOAD_FOLDER.
    Returns detection_type and result dict, or None, None if no detection.
    """
    if not POTHOLE_MODEL or not WASTE_MODEL:
        return None, None # Cannot proceed if models are not loaded

    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']

    # Ensure base upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Generate unique filenames
    timestamp = int(time.time())
    original_filename = image.filename
    temp_original_filename = f"{timestamp}_original_{original_filename}"
    temp_detected_filename = f"{timestamp}_detected_{original_filename}"

    temp_original_path = os.path.join(UPLOAD_FOLDER, temp_original_filename)
    
    # Save original uploaded image temporarily
    image.save(temp_original_path) 
    
    detection_found = False
    
    # ---------- Waste Detection ----------
    waste_results = WASTE_MODEL.predict(
        source=temp_original_path,
        save=False,
        conf=0.5 # Confidence threshold
    )

    if len(waste_results[0].boxes) > 0:
        detection_found = True
        first_class = int(waste_results[0].boxes.cls[0].item())
        
        # NOTE: Verify this CLASS_MAP against your trained model's classes.
        CLASS_MAP = {0: 'Glass', 1: 'Metal', 2: 'Paper', 3: 'Plastic', 4: 'Residual'}
        category = CLASS_MAP.get(first_class, 'Unknown')
        
        # Manually save the annotated image to the temporary folder
        temp_detected_path = os.path.join(UPLOAD_FOLDER, temp_detected_filename)
        waste_results[0].save(filename=temp_detected_path)

        return 'waste', {
            'image_name': temp_original_filename,
            'detected_image_path': temp_detected_filename, 
            'detection_status': f'{category} detected',
            'is_waste': True,
            'waste_category': category,
            'is_recyclable': category not in ['Residual', 'Paper'], # 'Paper' लाई recyclable मान्नुहुन्न भने यो तर्क ठीक छ
            'is_decomposable': category == 'Paper' # 'paper' लाई decomposable मानिएको छ
        }

    # ---------- Pothole Detection ----------
    pothole_results = POTHOLE_MODEL.predict(
        source=temp_original_path,
        save=False,
        conf=0.5 # Confidence threshold
    )

    if len(pothole_results[0].boxes) > 0:
        detection_found = True
        
        # Manually save the annotated image to the temporary folder
        temp_detected_path = os.path.join(UPLOAD_FOLDER, temp_detected_filename)
        pothole_results[0].save(filename=temp_detected_path)

        return 'pothole', {
            'image_name': temp_original_filename,
            'detected_image_path': temp_detected_filename, 
            'status': 'Pothole detected'
        }
    
    # Clean up: If no detection found, delete the original temporary file 
    # as the controller will not move it.
    if not detection_found and os.path.exists(temp_original_path):
        os.remove(temp_original_path)

    # --- No detection found in either model ---
    return None, None