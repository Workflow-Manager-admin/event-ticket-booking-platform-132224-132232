from app import create_app
from app.models import db

# PUBLIC_INTERFACE
def init_database():
    """
    Initializes the database and creates all tables using the production config.
    """
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created.")

if __name__ == "__main__":
    init_database()
