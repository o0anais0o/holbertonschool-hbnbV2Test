import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'cle_ultra_secrete'
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProdutionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
print("config.py exécuté")
