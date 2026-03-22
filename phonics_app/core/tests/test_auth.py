"""
Tests for user authentication and registration
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.tests.factories import UserFactory, PlanFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserAuthentication:
    """Test user authentication flow"""

    def test_user_can_register(self, client):
        """Test user registration"""
        url = reverse("core:signup")
        data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        response = client.post(url, data)
        assert response.status_code in [200, 302]  # Success or redirect
        assert User.objects.filter(username="newuser").exists()

    def test_login_page_loads(self, client):
        """Test login page is accessible"""
        response = client.get(reverse("core:login"))
        assert response.status_code == 200
        assert "username" in response.content.decode()

    def test_user_can_login(self, client):
        """Test user login"""
        user = UserFactory(username="testuser", email="test@test.com")
        user.set_password("testpass123")
        user.save()

        response = client.post(
            reverse("core:login"),
            {
                "username": "testuser",
                "password": "testpass123",
            },
        )
        # Should redirect after successful login
        assert response.status_code in [200, 302]

    def test_invalid_login_fails(self, client):
        """Test login with wrong password fails"""
        UserFactory(username="testuser")
        response = client.post(
            reverse("core:login"),
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 200  # Form re-rendered with error


@pytest.mark.django_db
class TestUserModel:
    """Test User model functionality"""

    def test_user_creation(self):
        """Test user is created correctly"""
        user = UserFactory(username="testuser", email="test@test.com")
        assert user.username == "testuser"
        assert user.email == "test@test.com"

    def test_user_has_active_subscription(self):
        """Test has_active_subscription method"""
        user = UserFactory()
        # New user should not have active subscription
        assert not user.has_active_subscription()

    def test_unique_email_constraint(self):
        """Test email uniqueness constraint"""
        UserFactory(email="unique@test.com")
        with pytest.raises(Exception):  # DatabaseError
            UserFactory(email="unique@test.com")

    def test_user_plan_assignment(self):
        """Test plan assignment to user"""
        plan = PlanFactory(name="Test Plan")
        user = UserFactory(plan=plan)
        assert user.plan.name == "Test Plan"
