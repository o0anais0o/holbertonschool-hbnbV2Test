from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import HBnBFacade

api = Namespace('amenities', description="Amenities operations")
facade = HBnBFacade()

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Amenity name')
})

@api.route('/')
class AmenityList(Resource):
    @api.doc('get_all_amenities')
    def get(self):
        """Liste toutes les amenities (public)"""
        amenities = facade.list_amenities()
        return [a.to_dict() for a in amenities], 200

    @api.expect(amenity_model)
    @jwt_required()
    def post(self):
        """Créer une nouvelle amenity (admin uniquement)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        data = api.payload
        if not data.get('name'):
            return {'error': 'Missing amenity name'}, 400

        # Vérifier unicité
        for a in facade.list_amenities():
            if a.name.lower() == data['name'].lower():
                return {'error': 'Amenity already exists'}, 400

        amenity = facade.create_amenity(data)
        return amenity.to_dict(), 201

@api.route('/<amenity_id>')
@api.param('amenity_id', 'L\'ID de l\'amenity')
class AmenityResource(Resource):
    @api.doc('get_amenity')
    def get(self, amenity_id):
        """Récupère une amenity par ID (public)"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return amenity.to_dict(), 200

    @api.expect(amenity_model)
    @jwt_required()
    def put(self, amenity_id):
        """Met à jour une amenity (admin uniquement)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        data = request.json
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404

        # Vérifier unicité si le nom change
        if 'name' in data and data['name'].lower() != amenity.name.lower():
            for a in facade.list_amenities():
                if a.name.lower() == data['name'].lower():
                    return {'error': 'Amenity already exists'}, 400

        updated = facade.update_amenity(amenity_id, data)
        return updated.to_dict(), 200

    @jwt_required()
    def delete(self, amenity_id):
        """Supprime une amenity (admin uniquement)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404

        facade.delete_amenity(amenity_id)
        return {}, 204
