from app import db
from app.models.base_model import BaseModel

class Place(BaseModel):
    __tablename__ = 'places'
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    # Relations
    reviews = db.relationship('Review', backref='place', lazy=True, cascade="all, delete-orphan")
    amenities = db.relationship('PlaceAmenity', back_populates='place', cascade="all, delete-orphan")

    def __init__(self, title, description, price, latitude, longitude, owner):
        super().__init__()
        if not title or len(title) > 100:
            raise ValueError("Title is required and must be <= 100 chars")
        if price is None or float(price) <= 0:
            raise ValueError("Price must be positive")
        if not (-90.0 <= float(latitude) <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0")
        if not (-180.0 <= float(longitude) <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0")
        if not owner:
            raise ValueError("Owner (User) is required")
        self.title = title
        self.description = description or ""
        self.price = float(price)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.owner_id = owner.id

class PlaceAmenity(db.Model):
    __tablename__ = 'place_amenity'
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), primary_key=True)
    amenity_id = db.Column(db.String(36), db.ForeignKey('amenities.id'), primary_key=True)
    place = db.relationship('Place', back_populates='amenities')
    amenity = db.relationship('Amenity', back_populates='places')
