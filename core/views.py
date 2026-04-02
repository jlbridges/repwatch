from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from smartystreets_python_sdk import request

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

# Helper function to build out hierarchial list for rep committee membership
def build_committee_tree(memberships):
    parents = {}
    ordered = []
    
    print("Building committee tree")

    for m in memberships:
        committee = m.committee

        if committee.is_subcommittee and committee.parent_committee:
            parent = committee.parent_committee
            parent_id = parent.committee_id

            if parent_id not in parents:
                parents[parent_id] = {
                    "committee": parent,
                    "role": None,
                    "rank": None,
                    "subs": []
                }
                ordered.append(parents[parent_id])

            parents[parent_id]["subs"].append({
                "committee": committee,
                "role": m.role,
                "rank": m.rank
            })

        else:
            cid = committee.committee_id

            if cid not in parents:
                entry = {
                    "committee": committee,
                    "role": m.role,
                    "rank": m.rank,
                    "subs": []
                }
                parents[cid] = entry
                ordered.append(entry)
            else:
                parents[cid]["role"] = m.role
                parents[cid]["rank"] = m.rank

    return ordered


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

    if address:
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

    representatives = list(
        Representative.objects
        .filter(constituents=user)
        .prefetch_related("rep_details", "committee_memberships__committee__parent_committee")
    )
    for rep in representatives:
        rep.committee_tree = build_committee_tree(rep.committee_memberships.all())

    return render(request, "core/dashboard.html", {
        "show_layout": True,
        "page": "dashboard",
        "representatives": representatives
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
@require_POST
def accountlogout(request):
    logout(request)
    return redirect("homepage")

