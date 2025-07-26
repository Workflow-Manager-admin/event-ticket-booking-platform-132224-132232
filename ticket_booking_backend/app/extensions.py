from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

# PUBLIC_INTERFACE
def init_jwt(app):
    """Bind JWTManager to the application."""
    jwt.init_app(app)
