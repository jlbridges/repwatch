# database models will be initialized here
from django.db import models
from django.contrib.auth.models import User 


class Profile(models.Model): 
    STATE_LIST = {
        "NC": "North Carolina",
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to auth user
    address_line1 = models.CharField(max_length=35, blank=False,null=False, default="")
    address_line2 = models.CharField(max_length=35, blank=True, default="")
    city = models.CharField(max_length=50, blank=False,null=False, default="")
    state = models.CharField(max_length=2,blank=False,null=False, choices=STATE_LIST)
    zipcode = models.CharField(max_length=10, blank=False,null=False,default="")

    class Meta:
        db_table = "repwatch_profile"
       

    def __str__(self):
        return f"{self.user.username}'s profile"


class representative(models.Model):
    Bioguide_id = models.CharField(max_length=10,blank=False, null=False, primary_key=True)
    constituents = models.ManyToManyField(User)
    name = models.CharField(max_length=70,blank=False)
    district_number = models.IntegerField(null=False)
    first_name = models.CharField(max_length=35,blank=False, null=False)
    last_name = models.CharField(max_length=35, blank=False,null=False)
    state = models.CharField(max_length=2, blank=False, null=False)
    party = models.CharField(max_length=25,blank= False)
    photo_url = models.URLField(max_length=40)
    image = models.ImageField()
    
    class Meta:
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["first_name"], name="first_name_idx"),
            models.Index(fields=["Bioguide_id"],name="Bio_idx"),
        ]
def __str(self):
    return f"{self.Bioguide_id}"
