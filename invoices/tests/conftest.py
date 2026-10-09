import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def user():
    return User.objects.create(username="quamobigs", password="testpass321")


@pytest.fixture
def other_user():
    return User.objects.create(username="testuser", password="testpass123")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client
