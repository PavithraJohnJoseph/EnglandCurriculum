"""
Tests for plan and subscription functionality
"""

import pytest
from django.urls import reverse
from core.models import Plan, Subscription
from core.tests.factories import UserFactory, PlanFactory
from datetime import timedelta
from django.utils import timezone


@pytest.mark.django_db
class TestPlans:
    """Test plan functionality"""

    def test_plan_creation(self):
        """Test plan is created correctly"""
        plan = PlanFactory(
            name="Gold Plan", price=9.99, access_years=[2012, 2013, 2014]
        )
        assert plan.name == "Gold Plan"
        assert float(plan.price) == 9.99
        assert plan.access_years == [2012, 2013, 2014]

    def test_plan_with_audio_enabled(self):
        """Test plan with audio enabled"""
        plan = PlanFactory(audio_enabled=True)
        assert plan.audio_enabled is True

    def test_free_plan(self):
        """Test free plan creation"""
        plan = PlanFactory(is_free=True, price=0)
        assert plan.is_free is True
        assert plan.price == 0

    def test_multiple_plans_exist(self):
        """Test multiple plans can exist"""
        PlanFactory(name="Bronze")
        PlanFactory(name="Silver")
        PlanFactory(name="Gold")
        assert Plan.objects.count() == 3


@pytest.mark.django_db
class TestSubscriptions:
    """Test subscription functionality"""

    def test_subscription_creation(self):
        """Test subscription is created correctly"""
        user = UserFactory()
        plan = PlanFactory()
        subscription = Subscription.objects.create(
            user=user, plan=plan, end_date=timezone.now().date() + timedelta(days=365)
        )
        assert subscription.user == user
        assert subscription.plan == plan
        assert subscription.active is True

    def test_subscription_validity(self):
        """Test subscription validity check"""
        user = UserFactory()
        plan = PlanFactory()
        subscription = Subscription.objects.create(
            user=user, plan=plan, end_date=timezone.now().date() + timedelta(days=365)
        )
        assert subscription.is_valid() is True

    def test_expired_subscription_invalid(self):
        """Test expired subscription is invalid"""
        user = UserFactory()
        plan = PlanFactory()
        subscription = Subscription.objects.create(
            user=user, plan=plan, end_date=timezone.now().date() - timedelta(days=1)
        )
        assert subscription.is_valid() is False

    def test_inactive_subscription_invalid(self):
        """Test inactive subscription is invalid"""
        user = UserFactory()
        plan = PlanFactory()
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            active=False,
            end_date=timezone.now().date() + timedelta(days=365),
        )
        assert subscription.is_valid() is False


@pytest.mark.django_db
class TestPlanSelection:
    """Test plan selection views"""

    def test_plan_selection_page_loads(self, client):
        """Test plan selection page is accessible"""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("core:plan_selection"))
        assert response.status_code == 200

    def test_plan_selection_displays_plans(self, client):
        """Test plan selection shows available plans"""
        user = UserFactory()
        PlanFactory(name="Free Plan", is_free=True)
        client.force_login(user)
        response = client.get(reverse("core:plan_selection"))
        assert response.status_code == 200
        assert b"Free Plan" in response.content
