from flask_restx import Namespace, Resource, fields
from app.services.auth import login_user  # ← appel au service

api = Namespace('auth', description='Auth operations')

login_model = api.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data = api.payload
        token = login_user(data['email'], data['password'])
        if not token:
            return {'error': 'Invalid credentials'}, 401
        return {'access_token': token}, 200
