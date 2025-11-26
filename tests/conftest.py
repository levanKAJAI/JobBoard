import pytest
from app import create_app,db
from app.models import User
from werkzeug.security import generate_password_hash
class TestConfig:
    SECRET_KEY='test'
    SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    WTF_CSRF_ENABLED=False
@pytest.fixture()
def app():
    app=create_app()
    app.config.from_object(TestConfig)
    with app.app_context():
        db.create_all()
        user=User(name='Test',email='test@test.com',password=generate_password_hash('password'))
        db.session.add(user)
        db.session.commit()
    yield app
@pytest.fixture()
def client(app):
    return app.test_client()
