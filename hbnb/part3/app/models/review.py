from app import db
from app.models.base_model import BaseModel

class Review(BaseModel):
    __tablename__ = 'reviews'
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    def __init__(self, text, rating, place, user):
        super().__init__()
        if not text:
            raise ValueError("Review text is required")
        if not (1 <= int(rating) <= 5):
            raise ValueError("Rating must be between 1 and 5")
        if not place:
            raise ValueError("Place is required")
        if not user:
            raise ValueError("User is required")
        self.text = text
        self.rating = int(rating)
        self.place_id = place.id
        self.user_id = user.id
