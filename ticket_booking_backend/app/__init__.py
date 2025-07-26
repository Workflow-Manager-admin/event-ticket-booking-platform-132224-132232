from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

from .routes.health import blp as health_blp
from .routes.auth import blp as auth_blp
from .routes.events import blp as events_blp
from .routes.tickets import blp as tickets_blp
from .routes.users import blp as users_blp
from .routes.bookings import blp as bookings_blp

from .models import db
from .extensions import init_jwt
from .config import configure_app

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["API_TITLE"] = "My Flask API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Environment/database/JWT
configure_app(app)
db.init_app(app)
init_jwt(app)

api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)
api.register_blueprint(events_blp)
api.register_blueprint(tickets_blp)
api.register_blueprint(users_blp)
api.register_blueprint(bookings_blp)
