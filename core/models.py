from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    STATE_LIST = (
        ("NC", "North Carolina"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    address_line1 = models.CharField(max_length=35)
    address_line2 = models.CharField(max_length=35, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2, choices=STATE_LIST)
    zipcode = models.CharField(max_length=10)

    class Meta:
        db_table = "repwatch_profile"

    def __str__(self):
        return f"{self.user.username}'s profile"


class Representative(models.Model):

    Bioguide_id = models.CharField(max_length=10, primary_key=True)

    # NEW FIELD Jacob asked for
    thomas_id = models.CharField(max_length=20, null=True, blank=True)

    constituents = models.ManyToManyField(User)
    name = models.CharField(max_length=70,blank=False)
    district_number = models.IntegerField(null=False)
    first_name = models.CharField(max_length=35,blank=False, null=False)
    last_name = models.CharField(max_length=35, blank=False,null=False)
    state = models.CharField(max_length=2, blank=False, null=False)
    party = models.CharField(max_length=25,blank= False)
    type = models.CharField(max_length=25, blank= False)
    photo_url = models.URLField(max_length=75)
    image = models.ImageField(default="default.jpg")  
    
    class Meta:
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["first_name"], name="first_name_idx"),
            models.Index(fields=["Bioguide_id"],name="Bio_idx"),
        ]
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class rep_detail(models.Model):
     Bioguide_id = models.ForeignKey(Representative, on_delete=models.CASCADE,related_name='rep_details')
     thomas_id = models.CharField(max_length=10,null=True,blank=True)
     currentMember = models.BooleanField()
     district_number = models.CharField(max_length=2,null=True,blank=True)
     congress = models.CharField(max_length=3,blank=True,null=True)
     state = models.CharField(max_length=2,blank=True,null=True)
     party = models.CharField(max_length=25,null=True,blank=True)
     type = models.CharField(max_length=15,null=True,blank=True)
     count_sponsoredLegislation = models.IntegerField(null=True,blank=True)
     count_cosponsoredLegislation = models.ImageField(null=True,blank=True)
     officialWebsiteUrl = models.URLField(max_length=50,null=True,blank=True)
     contact_form = models.CharField(max_length=20,null=True,blank=True)

     def __str__(self):
        return f"Details for{self.Bioguide_id}"
     
class committees(models.Model):
    committee_name = models.CharField(max_length=35,null=True,blank=True)
    rep_detail_id = models.ForeignKey(rep_detail, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.committee_name}"
    

class bill_headers:
    number = models.IntegerField(null=False, blank=True)
    congress = models.ImageField(null=False,blank=True)
    orginChamberCode = models.CharField(max_length=15,null=False,blank=True)
    type = models.CharField(max_length=10,null=False,blank=True)
    title = models.CharField(max_length=35,null=False,blank=True)

    def __str__(self):
        return f"{self.title}"
