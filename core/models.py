from django.conf import settings
from django.db import models


class Profile(models.Model):
    STATE_CHOICES = (
        ("NC", "NC"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default="NC")
    zip_code = models.CharField(max_length=10, blank=True, default="")

    def __str__(self):
        return f"{self.user} Profile"

