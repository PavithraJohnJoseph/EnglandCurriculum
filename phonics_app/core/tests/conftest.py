"""
Pytest configuration and fixtures
"""

import os
import pytest
from django.conf import settings


def pytest_configure():
    """Configure Django settings for testing"""
    # Disable HTTPS redirect for testing
    os.environ["DEBUG"] = "True"  # Tests run in debug mode
    settings.SECURE_SSL_REDIRECT = False


# Override client to disable SSL redirect
@pytest.fixture
def client():
    from django.test import Client

    client = Client(enforce_csrf_checks=False)
    return client
