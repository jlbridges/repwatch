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

    constituents = models.ManyToManyField(User)

    name = models.CharField(max_length=70)

    district_number = models.IntegerField(null=True, blank=True)

    first_name = models.CharField(max_length=35)

    last_name = models.CharField(max_length=35)

    state = models.CharField(max_length=2)

    party = models.CharField(max_length=25)

    type = models.CharField(max_length=25)

    photo_url = models.URLField(max_length=200)

    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class rep_detail(models.Model):

    Bioguide_id = models.ForeignKey(
        Representative,
        on_delete=models.CASCADE,
        related_name="rep_details"
    )

    currentMember = models.BooleanField(null=True, blank=True)

    district_number = models.CharField(max_length=2, null=True, blank=True)

    congress = models.CharField(max_length=3, null=True, blank=True)

    state = models.CharField(max_length=2, null=True, blank=True)

    party = models.CharField(max_length=25, null=True, blank=True)

    type = models.CharField(max_length=15, null=True, blank=True)

    count_sponsoredLegislation = models.IntegerField(null=True, blank=True)

    count_cosponsoredLegislation = models.IntegerField(null=True, blank=True)

    officalWebsiteUrl = models.URLField(max_length=200, null=True, blank=True)

    contract_form = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Details for {self.Bioguide_id}"