from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

blp = Blueprint("Users", "users", url_prefix="/users", description="User profile endpoints")

# PUBLIC_INTERFACE
@blp.route("/me")
class UserMe(MethodView):
    """Get the profile of the current user."""
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            abort(404, message="User not found")
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, 200
