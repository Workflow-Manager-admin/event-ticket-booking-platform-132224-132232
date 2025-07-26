from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token

from app.models import db, User

blp = Blueprint("Auth", "Authentication", url_prefix="/auth", description="User signup and login for authentication")

# PUBLIC_INTERFACE
@blp.route("/signup")
class Signup(MethodView):
    """
    User signup endpoint.

    Request body: { "username": str, "email": str, "password": str }
    Response: { "id": int, "username": str, "email": str }
    """
    def post(self):
        data = request.get_json()
        if not data or not data.get("username") or not data.get("email") or not data.get("password"):
            abort(400, message="Username, email and password required")
        if User.query.filter((User.username == data["username"]) | (User.email == data["email"])).first():
            abort(409, message="Username or email already exists")

        user = User(username=data["username"], email=data["email"])
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return {"id": user.id, "username": user.username, "email": user.email}, 201

# PUBLIC_INTERFACE
@blp.route("/login")
class Login(MethodView):
    """
    User login endpoint.

    Request body: { "username": str, "password": str }
    Response: { "access_token": str }
    """
    def post(self):
        data = request.get_json()
        if not data or not data.get("username") or not data.get("password"):
            abort(400, message="Username and password required")
        user = User.query.filter_by(username=data["username"]).first()
        if user is None or not user.check_password(data["password"]):
            abort(401, message="Invalid credentials")
        access_token = create_access_token(identity=user.id)
        return {"access_token": access_token}, 200
