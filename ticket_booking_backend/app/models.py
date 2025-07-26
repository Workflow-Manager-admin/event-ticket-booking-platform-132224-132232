from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# PUBLIC_INTERFACE
class User(db.Model):
    """User model for authentication and booking."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# PUBLIC_INTERFACE
class Event(db.Model):
    """Event model representing a bookable event."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    tickets = db.relationship('Ticket', backref='event', lazy=True)

# PUBLIC_INTERFACE
class Ticket(db.Model):
    """Ticket model linked to an event."""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    seat = db.Column(db.String(32), nullable=True)
    is_booked = db.Column(db.Boolean, default=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))

# PUBLIC_INTERFACE
class Booking(db.Model):
    """Booking model for storing user bookings."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    booked_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
