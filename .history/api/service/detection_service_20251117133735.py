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
try:
    POTHOLE_MODEL = YOLO(POTHOLE_MODEL_PATH)
    WASTE_MODEL = YOLO(WASTE_MODEL_PATH)
except Exception as e:
    print(f"Error loading models: {e}. Check your model paths.")
    POTHOLE_MODEL = None
    WASTE_MODEL = None


def detect_image_type(image):
    """
    पहिले पोटहोल पत्ता लगाउँछ, त्यसपछि फोहोर। अस्थायी रूपमा फाइलहरू बचत गर्छ।
    """
    if not POTHOLE_MODEL or not WASTE_MODEL:
        return None, None

    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # अद्वितीय अस्थायी फाइलनामहरू उत्पन्न गर्ने
    timestamp = int(time.time())
    original_filename_base = image.filename # मूल अपलोडको नाम
    temp_original_filename = f"{timestamp}_original_{original_filename_base}"
    temp_detected_filename = f"{timestamp}_detected_{original_filename_base}"

    temp_original_path = os.path.join(UPLOAD_FOLDER, temp_original_filename)
    
    # 1. मूल तस्बिरलाई अस्थायी पथमा बचत गर्ने (image stream पढ्ने)
    image.save(temp_original_path) 
    
    detection_found = False

    # ---------- Pothole Detection (उच्च प्राथमिकता) ----------
    pothole_results = POTHOLE_MODEL.predict(
        source=temp_original_path,
        save=False,
        conf=0.5 # आत्मविश्वासको सीमा (Confidence Threshold)
    )

    if len(pothole_results[0].boxes) > 0:
        detection_found = True
        
        # पत्ता लागेको तस्बिरलाई अस्थायी नामको साथ बचत गर्ने
        temp_detected_path = os.path.join(UPLOAD_FOLDER, temp_detected_filename)
        pothole_results[0].save(filename=temp_detected_path)

        return 'pothole', {
            'image_name': temp_original_filename,
            'detected_image_path': temp_detected_filename, # Controller ले यसलाई सार्छ
            'status': 'Pothole detected'
        }

    # ---------- Waste Detection (पोटहोल पत्ता नलागे मात्र) ----------
    waste_results = WASTE_MODEL.predict(
        source=temp_original_path,
        save=False,
        conf=0.5 # आत्मविश्वासको सीमा (Confidence Threshold)
    )

    if len(waste_results[0].boxes) > 0:
        detection_found = True
        first_class = int(waste_results[0].boxes.cls[0].item())
        
        # NOTE: तपाईंको मोडलको आधारमा CLASS_MAP इन्डेक्सहरू जाँच गर्नुहोस्
        CLASS_MAP = {0: 'Glass', 1: 'Metal', 2: 'Paper', 3: 'Plastic', 4: 'Residual'}
        category = CLASS_MAP.get(first_class, 'Unknown')
        
        # पत्ता लागेको तस्बिरलाई अस्थायी नामको साथ बचत गर्ने
        temp_detected_path = os.path.join(UPLOAD_FOLDER, temp_detected_filename)
        waste_results[0].save(filename=temp_detected_path)

        return 'waste', {
            'image_name': temp_original_filename,
            'detected_image_path': temp_detected_filename, # Controller ले यसलाई सार्छ
            'detection_status': f'{category} detected',
            'is_waste': True,
            'waste_category': category,
            'is_recyclable': category not in ['Residual'], # पेपरलाई decomposable/waste मान्दा
            'is_decomposable': category == 'Paper' # 'paper' लाई decomposable मानिएको छ
        }
    
    # यदि कुनै पत्ता लागेन भने, अस्थायी रूपमा बचत गरिएको मूल फाइल मेटाउने
    if not detection_found and os.path.exists(temp_original_path):
        os.remove(temp_original_path)

    # --- No detection found ---
    return None, None