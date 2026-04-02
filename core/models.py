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
    name = models.CharField(max_length=70, blank=False)
    district_number = models.IntegerField(null=False, default=0)
    first_name = models.CharField(max_length=35, blank=False, null=False)
    last_name = models.CharField(max_length=35, blank=False, null=False)
    state = models.CharField(max_length=2, blank=False, null=False)
    party = models.CharField(max_length=25, blank=False)
    type = models.CharField(max_length=25, blank=False)
    photo_url = models.URLField(max_length=200)
    image = models.ImageField(default="default.jpg")

    class Meta:
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["first_name"], name="first_name_idx"),
            models.Index(fields=["Bioguide_id"], name="Bio_idx"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class rep_detail(models.Model):
    Bioguide_id = models.ForeignKey(
        Representative,
        on_delete=models.CASCADE,
        related_name="rep_details"
    )
    thomas_id = models.CharField(max_length=10, null=True, blank=True)
    currentMember = models.BooleanField(blank=True, null=True)
    congress = models.IntegerField(null=True, blank=True)
    count_sponsoredLegislation = models.IntegerField(null=True, blank=True)
    count_cosponsoredLegislation = models.IntegerField(null=True, blank=True)
    officialWebsiteUrl = models.URLField(max_length=200, null=True, blank=True)
    contact_form = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Details for {self.Bioguide_id}"


class Committee(models.Model):
    committee_id = models.CharField(max_length=20, primary_key=True)

    committee_name = models.CharField(max_length=255, null=True, blank=True)
    committee_type = models.CharField(max_length=20, null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    parent_committee = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subcommittees"
    )

    is_subcommittee = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.committee_id} - {self.committee_name}"
    
class CommitteeMembership(models.Model):
    representative = models.ForeignKey(
        "Representative",
        on_delete=models.CASCADE,
        related_name="committee_memberships"
    )
    committee = models.ForeignKey(
        Committee,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.CharField(max_length=50, null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)

    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "repwatch_committee_membership"
        unique_together = ("representative", "committee")
        indexes = [
            models.Index(fields=["representative"]),
            models.Index(fields=["committee"]),
        ]

    def __str__(self):
        return f"{self.representative_id} -> {self.committee_id}"


class BillHeader(models.Model):
    number = models.IntegerField(null=False, blank=True)
    congress = models.IntegerField(null=False, blank=True)
    originChamberCode = models.CharField(max_length=15, null=False, blank=True)
    type = models.CharField(max_length=10, null=False, blank=True)
    title = models.CharField(max_length=200, null=False, blank=True)

    def __str__(self):
        return f"{self.title}"
    

#added in BillDeatil model to store the details of the bill
#linked it with a foreign key relationship to BillHeader
class BillDetail(models.Model):
    bill_header = models.ForeignKey(
        BillHeader,
        on_delete=models.CASCADE,
        related_name="bill_details"
    )

    number = models.IntegerField(blank=True)
    type = models.CharField(max_length=10, blank=True)
    congress = models.IntegerField(blank=True)
    introducedDate = models.DateField(null=True, blank=True)

    bill_subject = models.CharField(max_length=100, null=True, blank=True)

    sponsor_bioguideId = models.CharField(max_length=10, blank=True)
    firstName = models.CharField(max_length=35, blank=True)
    lastName = models.CharField(max_length=35, blank=True)
    party = models.CharField(max_length=20, blank=True)

    bill_summary = models.CharField(max_length=200, blank=True)

    originChamber = models.CharField(max_length=15, blank=True)
    currentChamber = models.CharField(max_length=15, blank=True)

    actionDesc = models.CharField(max_length=50, blank=True)
    bill_status = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.type} {self.number}"
    
    
class DataSourceState(models.Model):
    key = models.CharField(max_length=100, unique=True)
    checksum = models.CharField(max_length=64)
    updated_at = models.DateTimeField(auto_now=True)