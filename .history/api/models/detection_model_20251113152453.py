from database import db
from datetime import datetime

class Detection(db.Model):
    __tablename__ = 'detections'

    id = db.Column(db.Integer, primary_key=True)
    detection_type = db.Column(db.String(50), nullable=False)  # pothole or waste
    image_name = db.Column(db.String(255), nullable=False)
    detected_image_path = db.Column(db.String(255))
    location = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "detection_type": self.detection_type,
            "image_name": self.image_name,
            "detected_image_path": self.detected_image_path,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status
        }