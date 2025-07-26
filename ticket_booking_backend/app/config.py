import os

# PUBLIC_INTERFACE
def get_database_uri():
    """
    Constructs the database URI from environment variables.
    """
    # Expecting: MYSQL_URL, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT
    user = os.environ.get("MYSQL_USER")
    password = os.environ.get("MYSQL_PASSWORD")
    host = os.environ.get("MYSQL_URL")
    db = os.environ.get("MYSQL_DB")
    port = os.environ.get("MYSQL_PORT", 3306)
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

# PUBLIC_INTERFACE
def configure_app(app):
    """Set config for Flask app from environment."""
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "change_this_secret")
    app.config["PROPAGATE_EXCEPTIONS"] = True
