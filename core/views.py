from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from smartystreets_python_sdk import request
from django.db import transaction

from .forms import CustomUserRegister, EmailLoginForm
from .services.geocodio_service import get_representatives_from_address
from core.services.congress_service import get_member_details
from .models import BillHeader, Representative, Profile, rep_detail


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
        profile = None     #handling none returns in test cases where profile is not created yet
    
    #removed for testing to handle no profile existing

    if profile:
        address = f"{profile.address_line1}, {profile.city}, {profile.state} {profile.zipcode}"
    else:        
        address = None

    #Testing fixes for guarding API calls with try/except and handling None returns

    #Changing code to only make api calls if no reps exist.
    #This is to make sure it only does the call on login.

    existing_reps = Representative.objects.filter(constituents=user)

    if not existing_reps.exists() and address:
        try:
            reps_data = get_representatives_from_address(address)
        except Exception:
            reps_data = []
    else:
        reps_data = []

    #removed duplicate API call

    for rep in reps_data:
        rep_obj, _ = Representative.objects.update_or_create(
            Bioguide_id=rep["bioguide_id"],
            defaults={
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

        print("MEMBER DETAILS:", member_details)

        if member_details is None:
            member_details = {}

        rep_detail.objects.update_or_create(
            Bioguide_id=rep_obj,
            defaults={
                "currentMember": member_details.get("current_member") or False,
                "congress": member_details.get("congress"),
                "count_sponsoredLegislation": member_details.get("sponsored_legislation") or 0,
                "count_cosponsoredLegislation": member_details.get("cosponsored_legislation") or 0,
                "officialWebsiteUrl": member_details.get("official_website"),
                "contact_form": member_details.get("contact_form"),
            }
        )

        rep_obj.constituents.add(user)

    reps = Representative.objects.filter(constituents=user).prefetch_related("rep_details")

    #search
    q = request.GET.get("q")
    congress = request.GET.get("congress")
    bill_type = request.GET.get("bill_type")

    bills = BillHeader.objects.all()

    if q:
        bills = bills.filter(title__icontains=q)

    if congress:
        bills = bills.filter(congress=int(congress))

    if bill_type:
        bills = bills.filter(type=bill_type)

    return render(request, "core/dashboard.html", {
        "show_layout": True,
        "page": "dashboard",
        "reps": reps,
        #adding in for bill search
        "bills": bills,
    })


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
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
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

# Update to clear reps on logout so a fresh call may be made on login.

@require_POST
def accountlogout(request):
    if request.user.is_authenticated:
        user = request.user

        # Remove user from representatives (ManyToMany)
        reps = Representative.objects.filter(constituents=user)

        for rep in reps:
            rep.constituents.remove(user)

            # OPTIONAL: delete rep if no more users attached
            if rep.constituents.count() == 0:
                rep.delete()

    logout(request)
    return redirect("homepage")