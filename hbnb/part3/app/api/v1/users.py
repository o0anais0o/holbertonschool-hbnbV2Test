from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import HBnBFacade

api = Namespace('users', description="User operations")
facade = HBnBFacade()

user_model = api.model('User', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model)
    def post(self):
        data = api.payload
        if facade.get_user_by_email(data['email']):
            return {'error': 'Email already registered'}, 400
        user = facade.create_user(data)
        return user.to_dict(), 201

@api.route('/<user_id>')
class UserResource(Resource):
    @jwt_required()
    def get(self, user_id):
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @jwt_required()
    def put(self, user_id):
        current_user = get_jwt_identity()
        if current_user['id'] != user_id and not current_user.get('is_admin', False):
            return {'error': 'Unauthorized action'}, 403
        data = request.json
        if 'email' in data or 'password' in data:
            return {'error': 'You cannot modify email or password.'}, 400
        user = facade.update_user(user_id, data)
        return user.to_dict(), 200
