from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import CustomUserRegister, EmailLoginForm
from .services.geocodio_service import get_representatives_from_address
from core.services.congress_service import get_member_details
from .models import Representative, Profile, rep_detail


# Homepage
def homepage(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "homepage.html", {
        "show_layout": True,
        "page": "homepage"
    })


# Dashboard
@login_required
def dashboard(request):
    user = request.user

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return render(request, "core/dashboard.html", {
            "show_layout": True,
            "page": "dashboard"
        })

    address = f"{profile.address_line1}, {profile.city}, {profile.state} {profile.zipcode}"

    try:
        reps_data = get_representatives_from_address(address)
    except Exception as e:
        print("GEOCODIO ERROR:", e)
        reps_data = []

    for rep in reps_data:
        rep_obj, _ = Representative.objects.update_or_create(
            Bioguide_id=rep["bioguide_id"],
            defaults={
               #"thomas_id": rep.get("thomas_id"),
                "name": rep["name"],
                "district_number": rep.get("district_number"),
                "first_name": rep["first_name"],
                "last_name": rep["last_name"],
                "state": profile.state,
                "party": rep["party"],
                "type": rep["type"],
                "photo_url": rep["photo_url"],
            }
        )

        try:
            member_details = get_member_details(rep["bioguide_id"])
        except Exception as e:
            print("CONGRESS API ERROR:", e)
            member_details = {}

        if member_details is None:
            member_details = {}

        rep_detail.objects.update_or_create(
            Bioguide_id=rep_obj,
            defaults={
                "currentMember": member_details.get("currentMember", True), #congress
               # "district_number": member_details.get("district"), # reps model
                #"congress": member_details.get("congress"), # reps model
                # "state": member_details.get("state"), # reps model
                # "party": member_details.get("party"), reps model
                # "type": member_details.get("type"), reps model
                "count_sponsoredLegislation": member_details.get("sponsoredLegislation", {}).get("count", 0), # congress
                "count_cosponsoredLegislation": member_details.get("cosponsoredLegislation", {}).get("count", 0), # congress
                "officialWebsiteUrl": member_details.get("officialWebsiteUrl"), #congress
                "contact_form": member_details.get("contact_form"), #geocodio
            }
        )

        rep_obj.constituents.add(user)

    # Fetch all representatives for this user (with related rep_details)
    reps = Representative.objects.filter(constituents=user).prefetch_related('rep_details')

    return render(request, "core/dashboard.html", {
        "show_layout": True,
        "page": "dashboard",
        "reps": reps
    })


# Representative Detail Page
@login_required
# def representative_detail(request, bioguide_id):

#     rep = get_object_or_404(Representative, Bioguide_id=bioguide_id)

#     print("BIOGUIDE:", bioguide_id)

#     try:
#         member_details = get_member_details(bioguide_id)
#     except Exception as e:
#         print("CONGRESS API ERROR:", e)
#         member_details = None

#     print("MEMBER DETAILS:", member_details)

#     # Important: protect against None
#     if member_details is None:
#         member_details = {}

#     rep_detail.objects.update_or_create(
#         Bioguide_id=rep,
#         defaults={
#             "currentMember": member_details.get("currentMember"),
#             "district_number": member_details.get("district"),
#             "congress": member_details.get("congress"),
#             "state": member_details.get("state"),
#             "party": member_details.get("party"),
#             "type": member_details.get("type"),
#             "count_sponsoredLegislation": member_details.get("sponsoredLegislation", {}).get("count"),
#             "count_cosponsoredLegislation": member_details.get("cosponsoredLegislation", {}).get("count"),
#             "officialWebsiteUrl": member_details.get("officialWebsiteUrl"),
#             "contact_form": member_details.get("contact_form"),
#         }
#     )

#     print("REP DETAIL SAVED")

#     context = {
#         "rep": rep,
#         "member_details": member_details,
#         "show_layout": True,
#         "page": "rep_detail"
#     }

#     # return render(request, "core/rep_detail.html", context)


# About
def about(request):
    return render(request, "about.html", {
        "show_layout": True,
        "page": "about",
    })


# Registration
def registration(request):
    if request.method == "POST":
        form = CustomUserRegister(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("dashboard")

    else:
        form = CustomUserRegister()

    return render(request, "signup.html", {
        "form": form,
        "show_layout": True,
        "page": "signup",
    })


# Login
def login_view(request):
    if request.method == "POST":
        form = EmailLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect("dashboard")
            else:
                form.add_error(None, "Invalid email or password")
    else:
        form = EmailLoginForm()

    return render(request, "login.html", {
        "form": form,
        "show_layout": True,
        "page": "login"
    })


# Logout
@require_POST
def accountlogout(request):
    logout(request)
    return redirect("homepage")