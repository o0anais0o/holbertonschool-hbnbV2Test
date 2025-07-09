from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import HBnBFacade

api = Namespace('places', description="Places operations")
facade = HBnBFacade()

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Titre'),
    'description': fields.String(required=False, description='Description'),
    'price': fields.Float(required=True, description='Prix par nuit'),
    'latitude': fields.Float(required=False, description='Latitude'),
    'longitude': fields.Float(required=False, description='Longitude')
})

@api.route('/')
class PlaceList(Resource):
    @api.doc('get_all_places')
    def get(self):
        """Liste tous les lieux (public)"""
        places = facade.list_places()
        return [p.to_dict() for p in places], 200

    @api.expect(place_model)
    @jwt_required()
    def post(self):
        """Créer un nouveau lieu (utilisateur authentifié)"""
        current_user = get_jwt_identity()
        data = api.payload
        # Ajoute l'owner automatiquement
        data['user_id'] = current_user['id']
        place = facade.create_place(data)
        return place.to_dict(), 201

@api.route('/<place_id>')
@api.param('place_id', "ID du lieu")
class PlaceResource(Resource):
    @api.doc('get_place')
    def get(self, place_id):
        """Récupère un lieu par ID (public)"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return place.to_dict(), 200

    @api.expect(place_model)
    @jwt_required()
    def put(self, place_id):
        """Met à jour un lieu (owner ou admin uniquement)"""
        current_user = get_jwt_identity()
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        is_admin = current_user.get('is_admin', False)
        is_owner = place.user_id == current_user['id']
        if not (is_admin or is_owner):
            return {'error': 'Unauthorized action'}, 403

        data = request.json
        updated = facade.update_place(place_id, data)
        return updated.to_dict(), 200

    @jwt_required()
    def delete(self, place_id):
        """Supprime un lieu (owner ou admin uniquement)"""
        current_user = get_jwt_identity()
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        is_admin = current_user.get('is_admin', False)
        is_owner = place.user_id == current_user['id']
        if not (is_admin or is_owner):
            return {'error': 'Unauthorized action'}, 403

        facade.delete_place(place_id)
        return {}, 204
