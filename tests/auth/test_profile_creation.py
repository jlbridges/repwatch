import pytest
from django.contrib.auth.models import User
from core.models import Profile

@pytest.mark.django_db
def test_profile_created_on_user_creation():
    user = User.objects.create_user(username="test", password="pass")
    profile = Profile.objects.get(user=user)
    assert profile is not None