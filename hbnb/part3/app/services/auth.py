from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services.facade import HBnBFacade
from werkzeug.security import check_password_hash

api = Namespace('auth', description='Authentication')

login_model = api.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

def login_user(email, password):
    # Ici, ta logique pour vérifier l'utilisateur et retourner un token
    # Pour le test, tu peux juste retourner une chaîne bidon
    if email == "test@example.com" and password == "test":
        return "fake-jwt-token"
    return None

@api.route('/login')
class Login(Resource):
    @api.expect(login_model, validate=True)
    def post(self):
        data = api.payload
        facade = HBnBFacade()
        user = facade.get_user_by_email(data['email'])
        if not user or not user.check_password(data['password']):
            return {'error': 'Invalid credentials'}, 401
        token = create_access_token(identity=user.id, additional_claims={'is_admin': user.is_admin})
        return {'access_token': token}, 200
