# database models will be initialized here
from django.db import models
from django.contrib.auth.models import User 


class Profile(models.Model): 
    STATE_LIST = {
        "NC": "North Carolina",
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to auth user
    address_line1 = models.CharField(max_length=35, blank=True, default="")
    address_line2 = models.CharField(max_length=35, blank=True, default="")
    city = models.CharField(max_length=50, blank=True, default="")
    state = models.CharField(max_length=2, choices=STATE_LIST)
    zipcode = models.CharField(max_length=10, blank=True, default="")

    class Meta:
        db_table = "repwatch_profile"
       

    def __str__(self):
        return f"{self.user.username}'s profile"