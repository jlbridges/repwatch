from django.contrib.auth import login, logout
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
        reps = get_representatives_from_address(address)
    except Exception as e:
        print("GEOCODIO ERROR:", e)
        reps = None

    if reps:
        for rep in reps:

            rep_obj, created = Representative.objects.update_or_create(
                Bioguide_id=rep["bioguide_id"],
                defaults={
                    "thomas_id": rep.get("thomas_id"),   # NEW FIELD
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

            rep_obj.constituents.add(user)

    return render(request, "core/dashboard.html", {
        "show_layout": True,
        "page": "dashboard"
    })


# Representative Detail Page
@login_required
def representative_detail(request, bioguide_id):

    rep = get_object_or_404(Representative, Bioguide_id=bioguide_id)

    print("BIOGUIDE:", bioguide_id)

    try:
        member_details = get_member_details(bioguide_id)
    except Exception as e:
        print("CONGRESS API ERROR:", e)
        member_details = None

    print("MEMBER DETAILS:", member_details)

    if member_details is None:
        member_details = {}

    rep_detail.objects.update_or_create(
        Bioguide_id=rep,
        defaults={
            "currentMember": member_details.get("currentMember"),
            "district_number": member_details.get("district"),
            "congress": member_details.get("congress"),
            "state": member_details.get("state"),
            "party": member_details.get("party"),
            "type": member_details.get("type"),
            "count_sponsoredLegislation": member_details.get("sponsoredLegislation", {}).get("count"),
            "count_cosponsoredLegislation": member_details.get("cosponsoredLegislation", {}).get("count"),
            "officalWebsiteUrl": member_details.get("officialWebsiteUrl"),
            "contract_form": member_details.get("contact_form"),
        }
    )

    print("REP DETAIL SAVED")

    context = {
        "rep": rep,
        "member_details": member_details,
        "show_layout": True,
        "page": "rep_detail"
    }

    return render(request, "core/rep_detail.html", context)


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
            form.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, form.user)
            return redirect("dashboard")

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