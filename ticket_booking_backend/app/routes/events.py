from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from app.models import db, Event

blp = Blueprint("Events", "events", url_prefix="/events", description="Events CRUD endpoints")

# PUBLIC_INTERFACE
@blp.route("/")
class EventList(MethodView):
    """Get all events / create new event."""
    def get(self):
        events = Event.query.all()
        return [ {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "date": e.date.isoformat()
        } for e in events], 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or not all(k in data for k in ["title", "date"]):
            abort(400, message="Title and date are required")
        event = Event(title=data["title"], description=data.get("description"), date=data["date"])
        db.session.add(event)
        db.session.commit()
        return {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "date": event.date.isoformat()
        }, 201

# PUBLIC_INTERFACE
@blp.route("/<int:event_id>")
class EventDetail(MethodView):
    """Get, update, or delete a specific event."""
    def get(self, event_id):
        event = Event.query.get(event_id)
        if not event:
            abort(404, message="Event not found")
        return {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "date": event.date.isoformat()
        }, 200

    @jwt_required()
    def put(self, event_id):
        event = Event.query.get(event_id)
        if not event:
            abort(404, message="Event not found")
        data = request.get_json()
        if "title" in data:
            event.title = data["title"]
        if "description" in data:
            event.description = data["description"]
        if "date" in data:
            event.date = data["date"]
        db.session.commit()
        return {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "date": event.date.isoformat()
        }, 200

    @jwt_required()
    def delete(self, event_id):
        event = Event.query.get(event_id)
        if not event:
            abort(404, message="Event not found")
        db.session.delete(event)
        db.session.commit()
        return {"message": "Event deleted"}, 200
