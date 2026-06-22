"""
Test suite for the Mergington High School API endpoints.
Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """
        Arrange: Client is set up
        Act: Make GET request to /activities
        Assert: Response contains all activities with correct structure
        """
        # Arrange
        expected_activity_count = 3
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_get_activities_contains_required_fields(self, client, fresh_activities):
        """
        Arrange: Client is set up
        Act: Get activities response
        Assert: Each activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_success(self, client, fresh_activities):
        """
        Arrange: A new email not yet registered for Chess Club
        Act: POST signup request
        Assert: Student is added and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify student was actually added
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity_name]
        assert new_email in updated_activity["participants"]
    
    def test_signup_duplicate_student_fails(self, client, fresh_activities):
        """
        Arrange: A student already registered for Chess Club
        Act: Attempt to signup the same student again
        Assert: 400 error returned with appropriate message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_activity_not_found(self, client, fresh_activities):
        """
        Arrange: An activity that doesn't exist
        Act: Attempt to signup for non-existent activity
        Assert: 404 error returned
        """
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_student_success(self, client, fresh_activities):
        """
        Arrange: A student currently registered for Chess Club
        Act: POST unregister request
        Assert: Student is removed and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify student was actually removed
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()[activity_name]
        assert email_to_remove not in updated_activity["participants"]
    
    def test_unregister_student_not_registered_fails(self, client, fresh_activities):
        """
        Arrange: A student not registered for Gym Class
        Act: Attempt to unregister them
        Assert: 400 error returned
        """
        # Arrange
        activity_name = "Gym Class"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_activity_not_found(self, client, fresh_activities):
        """
        Arrange: An activity that doesn't exist
        Act: Attempt to unregister from non-existent activity
        Assert: 404 error returned
        """
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Client is set up
        Act: Make GET request to /
        Assert: Response is a redirect to /static/index.html
        """
        # Arrange & Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
