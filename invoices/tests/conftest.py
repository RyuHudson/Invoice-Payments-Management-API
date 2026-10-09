import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def auth_client():
    user = User.objects.create(username="testuser", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)
    return client
