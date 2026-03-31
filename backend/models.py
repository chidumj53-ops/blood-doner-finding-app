from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Donor(db.Model):
    __tablename__ = "donors"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    city = db.Column(db.String(80), nullable=False, index=True)
    area = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=True)
    available = db.Column(db.Boolean, default=True)
    last_donated = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "blood_group": self.blood_group,
            "city": self.city,
            "area": self.area,
            "phone": self.phone,
            "email": self.email,
            "age": self.age,
            "gender": self.gender,
            "available": self.available,
            "last_donated": self.last_donated,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }