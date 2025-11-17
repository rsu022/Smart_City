from database import db
from datetime import datetime

class Pothole(db.Model):
    __tablename__ = 'potholes'
    id = db.Column(db.Integer, primary_key=True)
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
            "image_name": self.image_name,
            "detected_image_path": self.detected_image_path,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status
        }

class Waste(db.Model):
    __tablename__ = 'wastes'
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    detected_image_path = db.Column(db.String(255))
    location = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    detection_status = db.Column(db.String(100))
    is_waste = db.Column(db.Boolean, default=False)
    waste_category = db.Column(db.String(100))
    is_recyclable = db.Column(db.Boolean, default=False)
    is_decomposable = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "image_name": self.image_name,
            "detected_image_path": self.detected_image_path,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "detection_status": self.detection_status,
            "is_waste": self.is_waste,
            "waste_category": self.waste_category,
            "is_recyclable": self.is_recyclable,
            "is_decomposable": self.is_decomposable
        }
