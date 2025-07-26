import pytest
from app import create_app
from app.models import db

# Utilities to help with authentication headers etc.
def auth_header(token):
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def app():
    """
    Creates a Flask app instance in testing mode, with SQLite in-memory DB.
    """
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret",
        "PROPAGATE_EXCEPTIONS": True,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
    yield app
    # Clean db
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_data():
    return {"username": "testuser", "email": "test@example.com", "password": "password123"}

@pytest.fixture
def user_token(client, user_data):
    # Signup
    res = client.post("/auth/signup", json=user_data)
    assert res.status_code == 201
    # Login
    login_data = {"username": user_data["username"], "password": user_data["password"]}
    res = client.post("/auth/login", json=login_data)
    assert res.status_code == 200
    return res.get_json()["access_token"]

def test_health(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.get_json()["message"] == "Healthy"

# -------- AUTH -------------
def test_signup_success(client, user_data):
    res = client.post("/auth/signup", json=user_data)
    assert res.status_code == 201
    d = res.get_json()
    assert d["username"] == user_data["username"]
    assert d["email"] == user_data["email"]

def test_signup_duplicate(client, user_data):
    c = client
    res1 = c.post("/auth/signup", json=user_data)
    assert res1.status_code == 201
    res2 = c.post("/auth/signup", json=user_data)
    assert res2.status_code == 409

def test_signup_missing_fields(client):
    res = client.post("/auth/signup", json={"email": "a@b.com"})
    assert res.status_code == 400

def test_login_success(client, user_data):
    c = client
    c.post("/auth/signup", json=user_data)
    res = c.post("/auth/login", json={"username": user_data["username"], "password": user_data["password"]})
    assert res.status_code == 200
    assert "access_token" in res.get_json()

def test_login_invalid_creds(client, user_data):
    client.post("/auth/signup", json=user_data)
    res = client.post("/auth/login", json={"username": user_data["username"], "password": "wrong"})
    assert res.status_code == 401

def test_login_missing_fields(client):
    res = client.post("/auth/login", json={})
    assert res.status_code == 400

# -------- USERS -------------
def test_user_me_success(client, user_token):
    res = client.get("/users/me", headers=auth_header(user_token))
    assert res.status_code == 200
    data = res.get_json()
    assert "username" in data and data["username"] == "testuser"

def test_user_me_unauthorized(client):
    res = client.get("/users/me")
    assert res.status_code == 401

# -------- EVENTS (CRUD) -------------

def test_events_crud(client, user_token):
    # GET initially empty
    res0 = client.get("/events/")
    assert res0.status_code == 200 and res0.get_json() == []
    # POST (missing auth)
    res0b = client.post("/events/", json={"title": "Event1", "date": "2024-06-01T12:00:00"})
    assert res0b.status_code == 401
    # POST success
    ev_data = {"title": "Event1", "date": "2024-06-01T12:00:00"}
    res1 = client.post("/events/", json=ev_data, headers=auth_header(user_token))
    assert res1.status_code == 201
    event_id = res1.get_json()["id"]

    # GET list
    res2 = client.get("/events/")
    found = [e for e in res2.get_json() if e["id"] == event_id]
    assert found
    # GET detail
    res3 = client.get(f"/events/{event_id}")
    assert res3.status_code == 200
    # GET not found
    res3b = client.get("/events/1200")
    assert res3b.status_code == 404

    # PUT (update) missing auth
    res4 = client.put(f"/events/{event_id}", json={"description": "desc"})
    assert res4.status_code == 401
    # PUT success
    upd = {"title": "Event 1 Updated", "date": "2024-07-01T10:00:00"}
    res5 = client.put(f"/events/{event_id}", json=upd, headers=auth_header(user_token))
    assert res5.status_code == 200 and res5.get_json()["title"] == "Event 1 Updated"

    # DELETE missing auth
    res6 = client.delete(f"/events/{event_id}")
    assert res6.status_code == 401
    # DELETE success
    res7 = client.delete(f"/events/{event_id}", headers=auth_header(user_token))
    assert res7.status_code == 200
    # DELETE again
    res8 = client.delete(f"/events/{event_id}", headers=auth_header(user_token))
    assert res8.status_code == 404

# -------- TICKETS (CRUD) -----------
def test_tickets_crud(client, user_token):
    # Must create event first
    event = client.post("/events/", json={"title": "E1", "date": "2024-06-01T13:00:00"}, headers=auth_header(user_token)).get_json()
    event_id = event["id"]

    # GET all
    res0 = client.get("/tickets/")
    assert res0.status_code == 200 and isinstance(res0.get_json(), list)
    # POST ticket (missing auth)
    res0b = client.post("/tickets/", json={"event_id": event_id, "price": 10.0})
    assert res0b.status_code == 401
    # POST ticket success
    res1 = client.post("/tickets/", json={"event_id": event_id, "price": 15.50, "seat": "A1"}, headers=auth_header(user_token))
    assert res1.status_code == 201
    ticket_id = res1.get_json()["id"]

    # GET ticket detail
    res2 = client.get(f"/tickets/{ticket_id}")
    assert res2.status_code == 200

    # GET not found
    res2b = client.get("/tickets/99999")
    assert res2b.status_code == 404

    # PUT missing auth
    res3 = client.put(f"/tickets/{ticket_id}", json={"price": 22.0})
    assert res3.status_code == 401
    # PUT success
    res4 = client.put(f"/tickets/{ticket_id}", json={"seat": "B2"}, headers=auth_header(user_token))
    assert res4.status_code == 200 and res4.get_json()["seat"] == "B2"

    # DELETE missing auth
    res5 = client.delete(f"/tickets/{ticket_id}")
    assert res5.status_code == 401
    # DELETE success
    res6 = client.delete(f"/tickets/{ticket_id}", headers=auth_header(user_token))
    assert res6.status_code == 200
    # DELETE again
    res7 = client.delete(f"/tickets/{ticket_id}", headers=auth_header(user_token))
    assert res7.status_code == 404

def test_ticket_post_invalid_event(client, user_token):
    res = client.post("/tickets/", json={"event_id": 10332, "price": 15}, headers=auth_header(user_token))
    assert res.status_code == 404

def test_ticket_post_missing_fields(client, user_token):
    res = client.post("/tickets/", json={"price": 15}, headers=auth_header(user_token))
    assert res.status_code == 400

# -------- BOOKINGS ----------
def test_booking_lifecycle(client, user_token):
    # Create event & ticket
    event = client.post("/events/", json={"title": "E2", "date": "2024-06-01T14:00:00"}, headers=auth_header(user_token)).get_json()
    ticket = client.post("/tickets/", json={"event_id": event["id"], "price": 9.99}, headers=auth_header(user_token)).get_json()

    # GET bookings initially none
    res0 = client.get("/bookings/", headers=auth_header(user_token))
    assert res0.status_code == 200 and res0.get_json() == []

    # POST booking (missing ticket_id)
    res1 = client.post("/bookings/", json={}, headers=auth_header(user_token))
    assert res1.status_code == 400
    # POST booking with non-existent ticket
    res1b = client.post("/bookings/", json={"ticket_id": 99999}, headers=auth_header(user_token))
    assert res1b.status_code == 404
    # POST booking success
    res2 = client.post("/bookings/", json={"ticket_id": ticket["id"]}, headers=auth_header(user_token))
    assert res2.status_code == 201
    booking = res2.get_json()
    # POST same ticket again = already booked
    res3 = client.post("/bookings/", json={"ticket_id": ticket["id"]}, headers=auth_header(user_token))
    assert res3.status_code == 409

    # GET bookings now has one
    res4 = client.get("/bookings/", headers=auth_header(user_token))
    assert res4.status_code == 200 and len(res4.get_json()) == 1

    # DELETE booking, missing auth
    res5 = client.delete(f"/bookings/{booking['booking_id']}")
    assert res5.status_code == 401
    # DELETE booking success
    res6 = client.delete(f"/bookings/{booking['booking_id']}", headers=auth_header(user_token))
    assert res6.status_code == 200
    # DELETE booking again = not found
    res7 = client.delete(f"/bookings/{booking['booking_id']}", headers=auth_header(user_token))
    assert res7.status_code == 404

def test_get_bookings_requires_auth(client):
    res = client.get("/bookings/")
    assert res.status_code == 401

def test_booking_only_own(client, user_token):
    # Create another user
    user2 = {"username": "u2", "email": "e2@example.com", "password": "pass222"}
    client.post("/auth/signup", json=user2)
    r2 = client.post("/auth/login", json={"username": "u2", "password": "pass222"})
    token2 = r2.get_json()["access_token"]
    # Create event, ticket
    event = client.post("/events/", json={"title": "E3", "date": "2024-11-22T04:21:00"}, headers=auth_header(user_token)).get_json()
    ticket = client.post("/tickets/", json={"event_id": event["id"], "price": 5.75}, headers=auth_header(user_token)).get_json()
    booking = client.post("/bookings/", json={"ticket_id": ticket["id"]}, headers=auth_header(user_token)).get_json()
    # User2 tries delete other's booking
    res = client.delete(f"/bookings/{booking['booking_id']}", headers=auth_header(token2))
    assert res.status_code == 404
