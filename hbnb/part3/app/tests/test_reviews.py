import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from app import create_app, db
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Crée un user
            user = User(first_name='Bob', last_name='Smith', email='bob@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            # Crée une amenity et un place
            amenity = Amenity(name='Wifi')
            db.session.add(amenity)
            db.session.commit()
            place = Place(
                title='Maison test',
                description='Description',
                price=100.0,
                latitude=1.0,
                longitude=1.0,
                owner_id=user.id
            )
            db.session.add(place)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def get_auth_token(client):
    client.post('/api/v1/users/', json={
        'first_name': 'Bob',
        'last_name': 'Smith',
        'email': 'bob@example.com',
        'password': 'password'
    })
    resp = client.post('/api/v1/auth/login', json={
        'email': 'bob@example.com',
        'password': 'password'
    })
    return resp.get_json()['access_token']

def test_create_review(client):
    token = get_auth_token(client)
    with client.application.app_context():
        user = User.query.filter_by(email='bob@example.com').first()
        place = Place.query.first()
        user_id = user.id
        place_id = place.id

    payload = {
        'text': 'Super séjour !',
        'rating': 5,
        'user_id': user_id,
        'place_id': place_id
    }
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.post('/api/v1/reviews/', json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['text'] == 'Super séjour !'
    assert data['user_id'] == user_id

def test_get_reviews(client):
    resp = client.get('/api/v1/reviews/')
    assert resp.status_code == 200

def test_create_review_invalid_rating(client):
    token = get_auth_token(client)
    with client.application.app_context():
        user = User.query.filter_by(email='bob@example.com').first()
        place = Place.query.first()
        user_id = user.id
        place_id = place.id

    payload = {
        'text': 'Bof',
        'rating': 10,  # Note invalide
        'user_id': user_id,
        'place_id': place_id
    }
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.post('/api/v1/reviews/', json=payload, headers=headers)
    print("STATUS CODE:", resp.status_code)
    print("RESPONSE JSON:", resp.json)
    assert resp.status_code == 400
