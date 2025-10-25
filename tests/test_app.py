import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Keep an original deep copy so tests can restore the in-memory DB
_original_activities = copy.deepcopy(activities)

import pytest


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before each test so tests are isolated."""
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))
    yield
    # cleanup (not strictly necessary because we reset at the start of each test)
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Keep an original deep copy so tests can restore the in-memory DB
_original_activities = copy.deepcopy(activities)

import pytest


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before each test so tests are isolated."""
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))
    yield
    # cleanup (not strictly necessary because we reset at the start of each test)
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Check a known activity exists
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_student@example.com"

    # Ensure the email is not already in participants
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Sign up (the endpoint expects the email in the request body as a raw JSON string)
    resp = client.post(f"/activities/{activity}/signup", json=email)
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Now the participant should be present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister using JSON body with an object (our endpoint accepts both styles)
    resp = client.post(f"/activities/{activity}/unregister", json={"email": email})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    # Verify removal
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_signup_duplicate_returns_400():
    activity = "Programming Class"
    email = "dup_student@example.com"

    # First signup should succeed
    resp = client.post(f"/activities/{activity}/signup", json=email)
    assert resp.status_code == 200

    # Second signup should fail with 400
    resp = client.post(f"/activities/{activity}/signup", json=email)
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"] or resp.json()["detail"]