from app import db
from app.models.base_model import BaseModel

class Amenity(BaseModel):
    __tablename__ = 'amenities'
    name = db.Column(db.String(50), nullable=False)
    places = db.relationship('PlaceAmenity', back_populates='amenity', cascade="all, delete-orphan")

    def __init__(self, name):
        super().__init__()
        if not name or len(name) > 50:
            raise ValueError("Amenity name is required and must be <= 50 chars")
        self.name = name
