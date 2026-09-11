import uuid
from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity state before and after each test."""
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))


def test_signup_adds_participant_to_activity():
    # Arrange
    activity_name = "Soccer Team"
    email = f"newstudent-{uuid.uuid4().hex}@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")

    # Assert
    assert response.status_code == 200

    activity = client.get("/activities").json()[activity_name]
    assert email in activity["participants"]


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    activity_name = "Soccer Team"
    email = f"newstudent-{uuid.uuid4().hex}@mergington.edu"
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={quote(email)}"
    )
    assert signup_response.status_code == 200

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{quote(email)}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    activity = client.get("/activities").json()[activity_name]
    assert email not in activity["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/Soccer Team/participants/{missing_email}")

    # Assert
    assert response.status_code == 404
