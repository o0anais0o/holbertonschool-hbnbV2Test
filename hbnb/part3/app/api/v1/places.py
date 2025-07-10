from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required

api = Namespace('places', description='Place operations')

amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(),
    'name': fields.String()
})

user_model = api.model('PlaceUser', {
    'id': fields.String(),
    'first_name': fields.String(),
    'last_name': fields.String(),
    'email': fields.String()
})

review_model = api.model('PlaceReview', {
    'id': fields.String(),
    'text': fields.String(),
    'rating': fields.Integer(),
    'user_id': fields.String()
})

place_model = api.model('Place', {
    'title': fields.String(required=True),
    'description': fields.String(),
    'price': fields.Float(required=True),
    'latitude': fields.Float(required=True),
    'longitude': fields.Float(required=True),
    'owner_id': fields.String(required=True),
    'amenities': fields.List(fields.String, required=True)
})

place_output_model = api.model('PlaceOut', {
    'id': fields.String(),
    'title': fields.String(),
    'description': fields.String(),
    'price': fields.Float(),
    'latitude': fields.Float(),
    'longitude': fields.Float(),
    'owner': fields.Nested(user_model),
    'amenities': fields.List(fields.Nested(amenity_model)),
    'reviews': fields.List(fields.Nested(review_model))
})

def place_to_dict(place, details=True):
    data = {
        'id': place.id,
        'title': place.title,
        'description': place.description,
        'price': place.price,
        'latitude': place.latitude,
        'longitude': place.longitude,
    }
    if details:
        data['owner'] = {
            'id': place.owner.id,
            'first_name': place.owner.first_name,
            'last_name': place.owner.last_name,
            'email': place.owner.email
        }
        data['amenities'] = [
            {'id': pa.amenity.id, 'name': pa.amenity.name}
            for pa in place.amenities
        ]
        data['reviews'] = [
            {
                'id': r.id,
                'text': r.text,
                'rating': r.rating,
                'user_id': r.user_id
            }
            for r in place.reviews
        ]
    return data

@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model, validate=True)
    @api.response(201, 'Place created')
    @api.response(400, 'Invalid input')
    @jwt_required()
    def post(self):
        data = api.payload
        try:
            place = HBnBFacade().create_place(data)
        except Exception as e:
            return {'error': str(e)}, 400
        return {"id": place.id, "title": place.title}, 201

    @api.marshal_list_with(place_output_model)
    def get(self):
        places = HBnBFacade().get_all_places()
        return [place_to_dict(p) for p in places], 200

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.marshal_with(place_output_model)
    def get(self, place_id):
        place = HBnBFacade().get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return place_to_dict(place), 200

    @api.expect(place_model, validate=True)
    @jwt_required()
    def put(self, place_id):
        data = api.payload
        try:
            place = HBnBFacade().update_place(place_id, data)
        except Exception as e:
            return {'error': str(e)}, 400
        if not place:
            return {'error': 'Place not found'}, 404
        return place_to_dict(place), 200

def get_auth_token(client):
    resp = client.post('/api/v1/users/', json={
        'first_name': 'Alice',
        'last_name': 'Doe',
        'email': 'alice@example.com',
        'password': 'password'
    })
    print("USER CREATION:", resp.status_code, resp.get_json())
    assert resp.status_code in (200, 201, 409), f"Erreur création user : {resp.data!r}"

    resp = client.post('/api/v1/auth/login', json={
        'email': 'alice@example.com',
        'password': 'password'
    })
    data = resp.get_json()
    print("LOGIN:", resp.status_code, data)
    assert data is not None, f"Pas de JSON dans la réponse login : {resp.data!r} (status {resp.status_code})"
    assert 'access_token' in data, f"Pas de access_token dans la réponse login : {data}"
    return data['access_token']
