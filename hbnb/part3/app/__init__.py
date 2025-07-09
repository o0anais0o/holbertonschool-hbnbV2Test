from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='default'):
    from config import config  # Ton fichier config.py
    from app.api.v1 import register_namespaces

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialisation des extensions
    db.init_app(app)
    jwt.init_app(app)

    # Création de l'API RESTx (doc sur /api/v1/)
    api = Api(
        app,
        version='1.0',
        title='HBNB API',
        description='API HBNB',
        doc='/api/v1/'
    )

    # Enregistrement des namespaces de l’API v1
    register_namespaces(api)

    return app
