from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import HBnBFacade

api = Namespace('reviews', description="Reviews operations")
facade = HBnBFacade()

review_model = api.model('Review', {
    'text': fields.String(required=True, description='Texte de l\'avis'),
    'rating': fields.Integer(required=True, description='Note (1-5)'),
    'place_id': fields.String(required=True, description='ID du lieu')
})

@api.route('/')
class ReviewList(Resource):
    @api.doc('get_all_reviews')
    def get(self):
        """Liste tous les avis (public)"""
        reviews = facade.list_reviews()
        return [r.to_dict() for r in reviews], 200

    @api.expect(review_model)
    @jwt_required()
    def post(self):
        """Créer un avis (utilisateur authentifié, 1 avis/lieu, pas sur ses propres lieux)"""
        current_user = get_jwt_identity()
        data = api.payload

        # Vérifier que le lieu existe
        place = facade.get_place(data['place_id'])
        if not place:
            return {'error': 'Place not found'}, 404

        # Pas d'avis sur son propre lieu
        if place.user_id == current_user['id']:
            return {'error': 'You cannot review your own place.'}, 400

        # Pas deux avis sur le même lieu
        user_reviews = [r for r in facade.list_reviews() if r.user_id == current_user['id'] and r.place_id == data['place_id']]
        if user_reviews:
            return {'error': 'You have already reviewed this place.'}, 400

        data['user_id'] = current_user['id']
        review = facade.create_review(data)
        return review.to_dict(), 201

@api.route('/<review_id>')
@api.param('review_id', "ID de l'avis")
class ReviewResource(Resource):
    @api.doc('get_review')
    def get(self, review_id):
        """Récupère un avis par ID (public)"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review.to_dict(), 200

    @api.expect(review_model)
    @jwt_required()
    def put(self, review_id):
        """Met à jour un avis (auteur ou admin uniquement)"""
        current_user = get_jwt_identity()
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        is_admin = current_user.get('is_admin', False)
        is_author = review.user_id == current_user['id']
        if not (is_admin or is_author):
            return {'error': 'Unauthorized action'}, 403

        data = request.json
        updated = facade.update_review(review_id, data)
        return updated.to_dict(), 200

    @jwt_required()
    def delete(self, review_id):
        """Supprime un avis (auteur ou admin uniquement)"""
        current_user = get_jwt_identity()
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        is_admin = current_user.get('is_admin', False)
        is_author = review.user_id == current_user['id']
        if not (is_admin or is_author):
            return {'error': 'Unauthorized action'}, 403

        facade.delete_review(review_id)
        return {}, 204
