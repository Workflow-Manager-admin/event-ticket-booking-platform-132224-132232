from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from app.models import db, Ticket, Event

blp = Blueprint("Tickets", "tickets", url_prefix="/tickets", description="Ticket management endpoints")

# PUBLIC_INTERFACE
@blp.route("/")
class TicketList(MethodView):
    """Get all available tickets or create a new one for an event."""
    def get(self):
        tickets = Ticket.query.all()
        return [ {
            "id": t.id,
            "event_id": t.event_id,
            "price": t.price,
            "seat": t.seat,
            "is_booked": t.is_booked
        } for t in tickets], 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or not all(k in data for k in ["event_id", "price"]):
            abort(400, message="event_id and price are required")
        event = Event.query.get(data["event_id"])
        if not event:
            abort(404, message="Event does not exist")
        # No date field expected for Ticket itself, so no conversion necessary here.
        ticket = Ticket(
            event_id=event.id,
            price=data["price"],
            seat=data.get("seat")
        )
        db.session.add(ticket)
        db.session.commit()
        return {
            "id": ticket.id,
            "event_id": ticket.event_id,
            "price": ticket.price,
            "seat": ticket.seat,
            "is_booked": ticket.is_booked
        }, 201

# PUBLIC_INTERFACE
@blp.route("/<int:ticket_id>")
class TicketDetail(MethodView):
    """Get, update, or delete a specific ticket."""
    def get(self, ticket_id):
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            abort(404, message="Ticket not found")
        return {
            "id": ticket.id,
            "event_id": ticket.event_id,
            "price": ticket.price,
            "seat": ticket.seat,
            "is_booked": ticket.is_booked
        }, 200

    @jwt_required()
    def put(self, ticket_id):
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            abort(404, message="Ticket not found")
        data = request.get_json()
        if "price" in data:
            ticket.price = data["price"]
        if "seat" in data:
            ticket.seat = data["seat"]
        db.session.commit()
        return {
            "id": ticket.id,
            "event_id": ticket.event_id,
            "price": ticket.price,
            "seat": ticket.seat,
            "is_booked": ticket.is_booked
        }, 200

    @jwt_required()
    def delete(self, ticket_id):
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            abort(404, message="Ticket not found")
        db.session.delete(ticket)
        db.session.commit()
        return {"message": "Ticket deleted"}, 200
