from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required, get_jwt

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True, description="Password (only for creation)")
})

user_output_model = api.model('UserOut', {
    'id': fields.String(),
    'first_name': fields.String(),
    'last_name': fields.String(),
    'email': fields.String()
})

def user_to_dict(user):
    return {
        'id': str(user.id),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    }

@api.route('/')
class UserList(Resource):
    @api.marshal_list_with(user_model)
    def get(self):
        users = HBnBFacade().get_all_users()
        return users
    @api.expect(user_model, validate=True)
    def post(self):
        data = api.payload
        try:
            user = HBnBFacade().create_user(data)
            return user, 201
        except Exception as e:
            return {'error': str(e)}, 400
    @api.response(201, 'User created')
    @api.response(400, 'Invalid input')
    @api.marshal_with(user_output_model, code=201)
    def post(self):
        data = api.payload
        try:
            user = HBnBFacade().create_user(data)
            return user_to_dict(user), 201
        except Exception as e:
            api.abort(400, str(e))

    @jwt_required()
    @api.marshal_list_with(user_output_model)
    def get(self):
        claims = get_jwt()
        if not claims.get('is_admin'):
            api.abort(403, 'Admin only')
        users = HBnBFacade().get_all_users()
        return [user_to_dict(u) for u in users], 200

@api.route('/<string:user_id>')
@api.param('user_id', 'The user identifier')
class UserResource(Resource):
    @jwt_required()
    @api.marshal_with(user_output_model)
    def get(self, user_id):
        user = HBnBFacade().get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        return user_to_dict(user), 200

    @jwt_required()
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_output_model)
    def put(self, user_id):
        data = api.payload
        try:
            user = HBnBFacade().update_user(user_id, data)
            if not user:
                api.abort(404, 'User not found')
            return user_to_dict(user), 200
        except Exception as e:
            api.abort(400, str(e))
