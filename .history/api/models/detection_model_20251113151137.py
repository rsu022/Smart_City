from waste_database import db   # or just 'database' if same db file
from datetime import datetime

# -------------------- Waste Detection Table --------------------
class WasteDetection(db.Model):
    __tablename__ = 'waste_detections'  # separate table for waste

    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    detected_image_path = db.Column(db.String(255))
    location = db.Column(db.String(255))        # garbage location
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(100))         # detection status

    def to_dict(self):
        return {
            "id": self.id,
            "image_name": self.image_name,
            "detected_image_path": self.detected_image_path,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status
        }

# -------------------- Pothole Detection Table --------------------
class PotholeDetection(db.Model):
    __tablename__ = 'pothole_detections'  # separate table for potholes

    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    detected_image_path = db.Column(db.String(255))
    location = db.Column(db.String(255))        # road location
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(100))         # detection status

    def to_dict(self):
        return {
            "id": self.id,
            "image_name": self.image_name,
            "detected_image_path": self.detected_image_path,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status
        }
