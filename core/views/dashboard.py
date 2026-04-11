from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.forms import User
from core.services.geocodio_service import get_representatives_from_address
from core.services.congress_service import get_member_details
from core.services.bill_service import get_bill_headers
from core.models import Representative, Profile, rep_detail

from .reps_helper import clear_user_reps
from .settings_helper import (
    check_Profile_changed,
    check_Account_changed,
    updateProfileData,
    updateUserData,
)


# Dashboard
@login_required
def dashboard(request):
    user = request.user
    profile = Profile.objects.get(user=user)


    try:
        profile = Profile.objects.get(user=user)
        if(request.POST.get('hidden_id')):
          user_id = request.POST.get('hidden_id')
          postedUser  = User.objects.get(pk=user_id)

        hasProfileChanged = check_Profile_changed(request)
        hasAccountChanged = check_Account_changed(request)

        if (hasProfileChanged):
           updateProfileData(profile, request)
           clear_user_reps(user)

        if (hasAccountChanged):
           updateUserData(postedUser, request)
           clear_user_reps(user)

           return redirect('dashboard')

    except Profile.DoesNotExist:
        profile = None     #handling none returns in test cases where profile is not created yet




    # 🔥 Call Bill API (working already)
    try:
     bills = get_bill_headers()
    except Exception as e:
        print("BILL API ERROR:", e)

    # =========================
    # ✅ BILL SEARCH (FIX TESTS)
    # =========================
    query = request.GET.get("q")
    congress = request.GET.get("congress")
    bill_type = request.GET.get("bill_type")

    #bills = BillHeader.objects.all()

    if query:
        bills = bills.filter(title__icontains=query)

    if congress:
        bills = bills.filter(congress=congress)

    if bill_type:
        bills = bills.filter(type=bill_type)
    print(bills)




    # 🔥 Build address
    address = f"{profile.address_line1}, {profile.city}, {profile.state} {profile.zipcode}"
   #print("ADDRESS:", address)

    # 🔥 Call Geocodio
    reps_data = get_representatives_from_address(address)
    #print("REPS DATA:", reps_data)

    # 🔥 Save representatives
    if not reps_data:
        reps_data = []

    for reps in reps_data:
        rep_obj, _ = Representative.objects.update_or_create(
            Bioguide_id=reps["bioguide_id"],
            defaults={
                "name": reps.get("name"),
                "district_number": reps.get("district_number"),
                "first_name": reps.get("first_name"),
                "last_name": reps.get("last_name"),
                "state": profile.state,
                "party": reps.get("party"),
                "type": reps.get("type"),
                "photo_url": reps.get("photo_url"),
            }
        )

        # 🔥 Congress API
        try:
            member_details = get_member_details(reps["bioguide_id"])
        except Exception as e:
            print("CONGRESS API ERROR:", e)
            member_details = {}

        rep_detail.objects.update_or_create(
            Bioguide_id=rep_obj,
            defaults={
                "currentMember": member_details.get("current_member") or False,
                "congress": member_details.get("congress"),
                "count_sponsoredLegislation": member_details.get("sponsored_legislation") or 0,
                "count_cosponsoredLegislation": member_details.get("cosponsored_legislation") or 0,
                "officialWebsiteUrl": member_details.get("official_website"),
            }
        )

        rep_obj.constituents.add(user)

    # 🔥 Fetch reps for display
    reps = Representative.objects.filter(constituents=user).prefetch_related("rep_details")

    return render(request, "core/dashboard.html", {
        "show_layout": True,
        "page": "dashboard",
        "reps": reps,
        "bills": bills,
    })
