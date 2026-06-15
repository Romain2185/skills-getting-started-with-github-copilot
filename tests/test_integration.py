"""
Integration tests for the activity management system.
These tests verify multi-step workflows and interactions between endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


class TestSignupAndDeleteWorkflow:
    """Integration tests combining signup and delete operations"""

    def test_signup_then_delete_workflow(self, client):
        """
        Arrange: Initialize app
        Act: 1) Sign up a student, 2) Verify they appear in activity, 3) Delete them
        Assert: Student successfully added then removed
        """
        # Arrange
        activity_name = "Basketball Club"
        email = "workflow@mergington.edu"

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200

        # Act - Verify in activity
        get_response = client.get("/activities")
        data = get_response.json()
        assert email in data[activity_name]["participants"]

        # Act - Delete
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert delete_response.status_code == 200

        # Assert - Verify removed
        get_response = client.get("/activities")
        data = get_response.json()
        assert email not in data[activity_name]["participants"]

    def test_multiple_signups_and_deletes(self, client):
        """
        Arrange: Initialize app
        Act: Sign up 3 students, verify all added, delete 2, verify count
        Assert: All operations succeed with correct state
        """
        # Arrange
        activity_name = "Debate Team"
        emails = [
            "debate1@mergington.edu",
            "debate2@mergington.edu",
            "debate3@mergington.edu"
        ]

        # Act - Sign up all
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert - All added
        get_response = client.get("/activities")
        data = get_response.json()
        current_count = len(data[activity_name]["participants"])
        assert current_count == 4  # 1 original + 3 new

        # Act - Delete 2 students
        for email in emails[:2]:
            response = client.delete(
                f"/activities/{activity_name}/participants/{email}"
            )
            assert response.status_code == 200

        # Assert - 2 deleted
        get_response = client.get("/activities")
        data = get_response.json()
        assert emails[0] not in data[activity_name]["participants"]
        assert emails[1] not in data[activity_name]["participants"]
        assert emails[2] in data[activity_name]["participants"]

    def test_capacity_tracking_after_operations(self, client):
        """
        Arrange: Initialize app with activity tracking
        Act: Sign up students and verify capacity tracking
        Assert: Spot counts reflect current participants
        """
        # Arrange
        activity_name = "Science Club"
        new_emails = [
            "science1@mergington.edu",
            "science2@mergington.edu"
        ]

        # Act - Get initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = len(initial_data[activity_name]["participants"])
        max_participants = initial_data[activity_name]["max_participants"]
        initial_spots = max_participants - initial_participants

        # Act - Sign up new students
        for email in new_emails:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )

        # Assert - Check updated capacity
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        updated_participants = len(updated_data[activity_name]["participants"])
        updated_spots = max_participants - updated_participants

        assert updated_participants == initial_participants + len(new_emails)
        assert updated_spots == initial_spots - len(new_emails)

    def test_same_student_different_activities(self, client):
        """
        Arrange: Initialize app
        Act: Sign up same student to multiple activities
        Assert: Student appears in all activities without conflict
        """
        # Arrange
        email = "versatile@mergington.edu"
        activities = ["Drama Club", "Art Club"]

        # Act - Sign up to multiple activities
        for activity_name in activities:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert - Student in all activities
        get_response = client.get("/activities")
        data = get_response.json()
        for activity_name in activities:
            assert email in data[activity_name]["participants"]

    def test_activity_data_consistency(self, client):
        """
        Arrange: Initialize app
        Act: Perform multiple signup/delete operations
        Assert: Activity data remains consistent (no corruption)
        """
        # Arrange
        activity_name = "Chess Club"
        operations = [
            ("signup", "user1@mergington.edu"),
            ("signup", "user2@mergington.edu"),
            ("delete", "user1@mergington.edu"),
            ("signup", "user3@mergington.edu"),
            ("delete", "user2@mergington.edu"),
        ]

        # Act - Perform operations
        for op_type, email in operations:
            if op_type == "signup":
                client.post(
                    f"/activities/{activity_name}/signup",
                    params={"email": email}
                )
            elif op_type == "delete":
                client.delete(
                    f"/activities/{activity_name}/participants/{email}"
                )

        # Assert - Verify final state
        get_response = client.get("/activities")
        data = get_response.json()
        activity = data[activity_name]

        # Check structure is intact
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

        # Check expected participants
        assert "user1@mergington.edu" not in activity["participants"]
        assert "user2@mergington.edu" not in activity["participants"]
        assert "user3@mergington.edu" in activity["participants"]
        # Original participants still there
        assert "michael@mergington.edu" in activity["participants"]
        assert "daniel@mergington.edu" in activity["participants"]


class TestErrorHandlingWorkflows:
    """Integration tests for error scenarios across workflows"""

    def test_cannot_signup_after_deletion(self, client):
        """
        Arrange: Student is registered for activity
        Act: Delete student, then try to sign up duplicate of a remaining participant
        Assert: Cannot create duplicate for remaining participant
        """
        # Arrange
        activity_name = "Programming Class"
        email_to_delete = "emma@mergington.edu"
        email_existing = "sophia@mergington.edu"

        # Act - Delete one participant
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_delete}"
        )
        assert delete_response.status_code == 200

        # Act - Try to sign up duplicate of remaining
        duplicate_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_existing}
        )

        # Assert - Duplicate signup fails
        assert duplicate_response.status_code == 400

    def test_delete_then_signup_then_delete_again(self, client):
        """
        Arrange: Initialize app
        Act: Delete → sign up same email → delete again
        Assert: All operations succeed in sequence
        """
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"

        # Act & Assert - First delete
        response1 = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert response1.status_code == 200

        # Act & Assert - Sign up
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response2.status_code == 200

        # Act & Assert - Delete again
        response3 = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert response3.status_code == 200

        # Verify final state
        get_response = client.get("/activities")
        data = get_response.json()
        assert email not in data[activity_name]["participants"]
