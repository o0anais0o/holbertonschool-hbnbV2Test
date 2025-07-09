from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required, get_jwt

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

user_output_model = api.model('UserOut', {
    'id': fields.String(),
    'first_name': fields.String(),
    'last_name': fields.String(),
    'email': fields.String()
})

def user_to_dict(user):
    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    }

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User created')
    @api.response(400, 'Invalid input')
    def post(self):
        data = api.payload
        try:
            user = HBnBFacade().create_user(data)
        except Exception as e:
            return {'error': str(e)}, 400
        return user_to_dict(user), 201

    @jwt_required()
    @api.marshal_list_with(user_output_model)
    def get(self):
        # Only admin can list all users
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin only'}, 403
        users = HBnBFacade().get_all_users()
        return [user_to_dict(u) for u in users], 200

@api.route('/<user_id>')
class UserResource(Resource):
    @jwt_required()
    @api.marshal_with(user_output_model)
    def get(self, user_id):
        user = HBnBFacade().get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user_to_dict(user), 200

    @jwt_required()
    @api.expect(user_model, validate=True)
    def put(self, user_id):
        data = api.payload
        try:
            user = HBnBFacade().update_user(user_id, data)
        except Exception as e:
            return {'error': str(e)}, 400
        if not user:
            return {'error': 'User not found'}, 404
        return user_to_dict(user), 200
