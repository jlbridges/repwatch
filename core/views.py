from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CustomUserRegister, EmailLoginForm
from .services.geocodio_service import get_representatives_from_address
from core.services.congress_service import get_member_details
from core.services.bill_service import get_bill_headers
from .models import Representative, Profile, rep_detail, BillHeader


def homepage(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "homepage.html", {
        "show_layout": True,
        "page": "homepage"
    })


@login_required
def dashboard(request):
    user = request.user

    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=user)

    # Handle POST (save address)
    if request.method == "POST":
        profile.address_line1 = request.POST.get("address_line1", "")
        profile.city = request.POST.get("city", "")
        profile.state = request.POST.get("state", "")
        profile.zipcode = request.POST.get("zipcode", "")
        profile.save()
        print("✅ Profile updated")

    # =========================
    # ✅ BILL API (SAFE)
    # =========================
    try:
        get_bill_headers()
    except Exception as e:
        print("BILL API ERROR:", e)

    # =========================
    # ✅ BILL SEARCH (FIX TESTS)
    # =========================
    query = request.GET.get("q")
    congress = request.GET.get("congress")
    bill_type = request.GET.get("bill_type")

    bills = BillHeader.objects.all()

    if query:
        bills = bills.filter(title__icontains=query)

    if congress:
        bills = bills.filter(congress=congress)

    if bill_type:
        bills = bills.filter(type=bill_type)

    # =========================
    # ADDRESS BUILD
    # =========================
    address = f"{profile.address_line1}, {profile.city}, {profile.state} {profile.zipcode}"
    print("ADDRESS:", address)

    # =========================
    # GEOCODIO API (SAFE)
    # =========================
    reps_data = get_representatives_from_address(address)

    if reps_data is None:
        reps_data = []

    print("REPS DATA:", reps_data)

    # =========================
    # SAVE REPS
    # =========================
    for rep in reps_data:

        if not rep.get("bioguide_id"):
            continue

        rep_obj, _ = Representative.objects.update_or_create(
            Bioguide_id=rep["bioguide_id"],
            defaults={
                "name": rep.get("name"),
                "district_number": rep.get("district_number"),
                "first_name": rep.get("first_name"),
                "last_name": rep.get("last_name"),
                "state": profile.state,
                "party": rep.get("party"),
                "type": rep.get("type"),
                "photo_url": rep.get("photo_url"),
            }
        )

        # =========================
        # CONGRESS API
        # =========================
        try:
            member_details = get_member_details(rep["bioguide_id"])
        except Exception:
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

    return render(request, "core/dashboard.html", {
        "show_layout": True,
        "page": "dashboard",
        "reps": reps,
        "bills": bills,  # ✅ IMPORTANT FOR TESTS
    })


def about(request):
    return render(request, "about.html", {
        "show_layout": True,
        "page": "about",
    })


def registration(request):
    if request.method == "POST":
        form = CustomUserRegister(request.POST)

        if form.is_valid():
            user = form.save()

            # ✅ FIX LOGIN BACKEND ERROR
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect("dashboard")
    else:
        form = CustomUserRegister()

    return render(request, "signup.html", {
        "form": form,
        "show_layout": True,
        "page": "signup",
    })


def login_view(request):
    if request.method == "POST":
        form = EmailLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=email, password=password)

            if user:
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


@require_POST
def accountlogout(request):
    # ✅ FIX: CLEAR USER REPS BEFORE LOGOUT
    if request.user.is_authenticated:
        reps = Representative.objects.filter(constituents=request.user)
        for rep in reps:
            rep.constituents.remove(request.user)

    logout(request)
    return redirect("homepage")