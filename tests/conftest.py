"""
Pytest configuration and fixtures for the activity management system tests.
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provide a TestClient for the FastAPI app.
    This creates a test client that can make requests to the app without running a server.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Provide a fresh copy of activities data for each test.
    This ensures test isolation - changes in one test don't affect others.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Outdoor soccer practices and interschool matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["alex@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Skill development, scrimmages, and friendly competitions",
            "schedule": "Mondays and Wednesdays, 5:00 PM - 6:30 PM",
            "max_participants": 15,
            "participants": ["nina@mergington.edu"]
        },
        "Art Club": {
            "description": "Painting, drawing, and mixed-media workshops",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["liam@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stagecraft, and production of school plays",
            "schedule": "Wednesdays and Saturdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debating, public speaking, and critical thinking",
            "schedule": "Thursdays, 3:45 PM - 5:15 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, science fairs, and research projects",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu"]
        }
    }
