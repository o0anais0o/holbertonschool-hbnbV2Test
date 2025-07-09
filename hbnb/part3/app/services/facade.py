from app.extensions import db
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.review import Review

class HBnBFacade:
    # ---------- USER ----------
    def create_user(self, data):
        User.validate_data(data)
        if User.query.filter_by(email=data['email']).first():
            raise ValueError("Email already registered")
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email']
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return user

    def get_user(self, user_id):
        return User.query.get(user_id)

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_all_users(self):
        return User.query.all()

    def update_user(self, user_id, data):
        user = self.get_user(user_id)
        if not user:
            return None
        if 'email' in data and data['email'] != user.email:
            if self.get_user_by_email(data['email']):
                raise ValueError("Email already registered")
            user.email = data['email']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'password' in data:
            user.set_password(data['password'])
        db.session.commit()
        return user

    # ---------- AMENITY ----------
    def create_amenity(self, data):
        if not data.get('name') or len(data['name']) > 50:
            raise ValueError("Amenity name is required and must be <= 50 chars")
        amenity = Amenity(name=data['name'])
        db.session.add(amenity)
        db.session.commit()
        return amenity

    def get_amenity(self, amenity_id):
        return Amenity.query.get(amenity_id)

    def get_all_amenities(self):
        return Amenity.query.all()

    def update_amenity(self, amenity_id, data):
        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return None
        if 'name' in data:
            if not data['name'] or len(data['name']) > 50:
                raise ValueError("Amenity name is required and must be <= 50 chars")
            amenity.name = data['name']
        db.session.commit()
        return amenity

    # ---------- PLACE ----------
    def create_place(self, data):
        owner = User.query.get(data['owner_id'])
        if not owner:
            raise ValueError("Owner not found")
        amenities = []
        for amenity_id in data.get('amenities', []):
            amenity = Amenity.query.get(amenity_id)
            if not amenity:
                raise ValueError(f"Amenity not found: {amenity_id}")
            amenities.append(amenity)
        place = Place(
            title=data['title'],
            description=data.get('description', ''),
            price=data['price'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            owner=owner
        )
        db.session.add(place)
        db.session.flush()  # Pour avoir l'ID du place

        # Ajout des amenities (table d'association)
        for amenity in amenities:
            pa = PlaceAmenity(place_id=place.id, amenity_id=amenity.id)
            db.session.add(pa)
        db.session.commit()
        return place

    def get_place(self, place_id):
        return Place.query.get(place_id)

    def get_all_places(self):
        return Place.query.all()

    def update_place(self, place_id, data):
        place = self.get_place(place_id)
        if not place:
            return None
        updatable = ['title', 'description', 'price', 'latitude', 'longitude']
        for key in updatable:
            if key in data:
                setattr(place, key, data[key])
        if 'owner_id' in data:
            owner = User.query.get(data['owner_id'])
            if not owner:
                raise ValueError("Owner not found")
            place.owner_id = owner.id
        if 'amenities' in data:
            # Supprimer les anciens liens
            PlaceAmenity.query.filter_by(place_id=place.id).delete()
            for amenity_id in data['amenities']:
                amenity = Amenity.query.get(amenity_id)
                if not amenity:
                    raise ValueError(f"Amenity not found: {amenity_id}")
                pa = PlaceAmenity(place_id=place.id, amenity_id=amenity.id)
                db.session.add(pa)
        db.session.commit()
        return place

    # ---------- REVIEW ----------
    def create_review(self, data):
        user = User.query.get(data['user_id'])
        if not user:
            raise ValueError("User not found")
        place = Place.query.get(data['place_id'])
        if not place:
            raise ValueError("Place not found")
        rating = data['rating']
        if not (1 <= int(rating) <= 5):
            raise ValueError("Rating must be between 1 and 5")
        review = Review(
            text=data['text'],
            rating=rating,
            place=place,
            user=user
        )
        db.session.add(review)
        db.session.commit()
        return review

    def get_review(self, review_id):
        return Review.query.get(review_id)

    def get_all_reviews(self):
        return Review.query.all()

    def get_reviews_by_place(self, place_id):
        place = Place.query.get(place_id)
        if not place:
            return None
        return place.reviews

    def update_review(self, review_id, data):
        review = self.get_review(review_id)
        if not review:
            return None
        if 'text' in data:
            review.text = data['text']
        if 'rating' in data:
            rating = data['rating']
            if not (1 <= int(rating) <= 5):
                raise ValueError("Rating must be between 1 and 5")
            review.rating = int(rating)
        db.session.commit()
        return review

    def delete_review(self, review_id):
        review = self.get_review(review_id)
        if not review:
            return False
        db.session.delete(review)
        db.session.commit()
        return True
