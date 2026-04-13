from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    # Arrange: No specific setup needed as data is in-memory

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check status code and response content
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_root_redirect():
    # Arrange: No setup needed

    # Act: Make GET request to /
    response = client.get("/")

    # Assert: Check for redirect or static file served (TestClient behavior)
    assert response.status_code == 200  # Assuming it serves the static file or follows
    # Note: In TestClient, redirects may be handled differently


def test_signup_success():
    # Arrange: Choose an activity and a new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Check success response
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}


def test_signup_activity_not_found():
    # Arrange: Use a non-existent activity
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act: Make POST request
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Check 404 error
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_already_signed_up():
    # Arrange: Sign up first, then try again
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})  # First signup

    # Act: Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Check 400 error
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_invalid_email():
    # Arrange: Use empty email
    activity_name = "Gym Class"
    email = ""

    # Act: Make POST request
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Since no validation, it should succeed (current behavior)
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}


def test_signup_beyond_max_participants():
    # Arrange: Sign up until over max (Chess Club max 12, has 2 already)
    activity_name = "Chess Club"
    emails = [f"extra{i}@mergington.edu" for i in range(15)]  # More than max

    # Act: Sign up all
    for email in emails:
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        # Current code allows it, so all should succeed
        assert response.status_code == 200

    # Assert: Check that participants list has grown beyond max
    response = client.get("/activities")
    data = response.json()
    participants = data[activity_name]["participants"]
    assert len(participants) > data[activity_name]["max_participants"]