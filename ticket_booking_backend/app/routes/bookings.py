from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import db, Booking, Ticket

blp = Blueprint("Bookings", "bookings", url_prefix="/bookings", description="Endpoints for ticket bookings")

# PUBLIC_INTERFACE
@blp.route("/")
class BookingList(MethodView):
    """GET all bookings for the current user, POST to create booking for ticket."""
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        bookings = Booking.query.filter_by(user_id=user_id).all()
        return [
            {
                "booking_id": b.id,
                "ticket_id": b.ticket_id,
                "booked_at": b.booked_at.isoformat()
            } for b in bookings
        ], 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        ticket_id = data.get("ticket_id")
        if not ticket_id:
            abort(400, message="ticket_id is required")
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            abort(404, message="Ticket does not exist")
        if ticket.is_booked:
            abort(409, message="Ticket is already booked")

        # Book the ticket
        booking = Booking(user_id=user_id, ticket_id=ticket_id)
        ticket.is_booked = True
        ticket.booking_id = booking.id
        db.session.add(booking)
        db.session.commit()
        return {
            "booking_id": booking.id,
            "ticket_id": booking.ticket_id,
            "booked_at": booking.booked_at.isoformat()
        }, 201

# PUBLIC_INTERFACE
@blp.route("/<int:booking_id>")
class BookingDetail(MethodView):
    """Cancel a booking (delete)."""
    @jwt_required()
    def delete(self, booking_id):
        user_id = get_jwt_identity()
        booking = Booking.query.get(booking_id)
        if not booking or booking.user_id != user_id:
            abort(404, message="Booking not found")
        ticket = Ticket.query.get(booking.ticket_id)
        if ticket:
            ticket.is_booked = False
            ticket.booking_id = None
        db.session.delete(booking)
        db.session.commit()
        return {"message": "Booking cancelled"}, 200
