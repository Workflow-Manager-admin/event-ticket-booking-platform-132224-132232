import os

# PUBLIC_INTERFACE
def get_database_uri():
    """
    Constructs the database URI from environment variables.
    Allows robust handling of potentially missing/empty values, especially MYSQL_PORT.
    """
    # Used for test configuration override:
    override_uri = os.environ.get("DATABASE_URI_OVERRIDE")
    if override_uri:
        return override_uri

    # Expecting: MYSQL_URL, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT
    user = os.environ.get("MYSQL_USER")
    password = os.environ.get("MYSQL_PASSWORD")
    host = os.environ.get("MYSQL_URL")
    db = os.environ.get("MYSQL_DB")
    port = os.environ.get("MYSQL_PORT", None)

    # Defensive handling for port:
    try:
        port = int(port) if port and str(port).strip() else 3306
    except Exception:
        port = 3306

    # Warn if construction might be invalid (dev-convenience)
    if not all([user, password, host, db]):
        raise RuntimeError("Some MySQL database environment variables are missing (MYSQL_USER, MYSQL_PASSWORD, MYSQL_URL, MYSQL_DB required)")

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

# PUBLIC_INTERFACE
def configure_app(app):
    """
    Set config for Flask app from environment.
    If SQLALCHEMY_DATABASE_URI is already provided (e.g., for testing), use it.
    """
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "change_this_secret")
    app.config["PROPAGATE_EXCEPTIONS"] = True
