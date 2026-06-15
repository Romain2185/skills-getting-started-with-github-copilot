"""
Unit tests for the activity management system API endpoints.
Tests follow the AAA (Arrange-Act-Assert) pattern for clarity.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirect(self, client):
        """
        Arrange: Initialize app with root endpoint
        Act: Make GET request to /
        Assert: Response redirects to /static/index.html
        """
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Initialize app with activities
        Act: Make GET request to /activities
        Assert: Response contains all activities with correct data
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9  # 9 activities total
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_contains_all_required_fields(self, client):
        """
        Arrange: Initialize app
        Act: Get activities
        Assert: Each activity has required fields
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_contains_participants(self, client):
        """
        Arrange: Initialize app with participants
        Act: Get activities
        Assert: Participants list is populated correctly
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert - verify some activities have participants
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_student_succeeds(self, client):
        """
        Arrange: Initialize app with Chess Club activity
        Act: Sign up a new student
        Assert: Response is successful and student is added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_participant_to_list(self, client):
        """
        Arrange: Initialize app
        Act: Sign up a student, then fetch activities
        Assert: Participant appears in the activity's participants list
        """
        # Arrange
        activity_name = "Soccer Team"
        email = "newsoccer@mergington.edu"

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")

        # Assert
        assert signup_response.status_code == 200
        data = activities_response.json()
        assert email in data[activity_name]["participants"]

    def test_signup_duplicate_student_fails(self, client):
        """
        Arrange: Initialize app with existing participant
        Act: Try to sign up the same student again
        Assert: Response is 400 Bad Request with error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_invalid_activity_fails(self, client):
        """
        Arrange: Initialize app
        Act: Try to sign up for non-existent activity
        Assert: Response is 404 Not Found
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_missing_email_parameter_fails(self, client):
        """
        Arrange: Initialize app
        Act: Try to sign up without email parameter
        Assert: Response is 422 Unprocessable Entity
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422  # Validation error

    def test_signup_multiple_different_students(self, client):
        """
        Arrange: Initialize app
        Act: Sign up multiple different students
        Assert: All are added successfully
        """
        # Arrange
        activity_name = "Art Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu"]

        # Act & Assert
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Verify all were added
        activities_response = client.get("/activities")
        data = activities_response.json()
        for email in emails:
            assert email in data[activity_name]["participants"]


class TestDeleteParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_delete_existing_participant_succeeds(self, client):
        """
        Arrange: Initialize app with existing participant
        Act: Delete the participant
        Assert: Response is successful
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_delete_removes_participant_from_list(self, client):
        """
        Arrange: Initialize app with participant
        Act: Delete participant, then fetch activities
        Assert: Participant no longer in list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"

        # Act
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        activities_response = client.get("/activities")

        # Assert
        assert delete_response.status_code == 200
        data = activities_response.json()
        assert email not in data[activity_name]["participants"]

    def test_delete_nonexistent_participant_fails(self, client):
        """
        Arrange: Initialize app
        Act: Try to delete participant not in activity
        Assert: Response is 404 Not Found
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_delete_from_invalid_activity_fails(self, client):
        """
        Arrange: Initialize app
        Act: Try to delete from non-existent activity
        Assert: Response is 404 Not Found
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_delete_multiple_participants(self, client):
        """
        Arrange: Initialize app with multiple participants
        Act: Delete each participant sequentially
        Assert: All are removed successfully
        """
        # Arrange
        activity_name = "Programming Class"
        participants_to_remove = [
            "emma@mergington.edu",
            "sophia@mergington.edu"
        ]

        # Act & Assert
        for email in participants_to_remove:
            response = client.delete(
                f"/activities/{activity_name}/participants/{email}"
            )
            assert response.status_code == 200

        # Verify all were removed
        activities_response = client.get("/activities")
        data = activities_response.json()
        for email in participants_to_remove:
            assert email not in data[activity_name]["participants"]

    def test_delete_then_readd_same_participant(self, client):
        """
        Arrange: Initialize app with participant
        Act: Delete participant, then sign them up again
        Assert: Both operations succeed
        """
        # Arrange
        activity_name = "Soccer Team"
        email = "alex@mergington.edu"

        # Act - Delete
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert delete_response.status_code == 200

        # Act - Re-add
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200

        # Assert - Participant is back
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data[activity_name]["participants"]
