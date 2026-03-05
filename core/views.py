from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .forms import CustomUserRegister, EmailLoginForm
from .services.geocodio_service import get_representatives_from_address
from .models import Representative, Profile


# Homepage
def homepage(request):
    context = {
        "show_layout": True,
        "page": "homepage"
    }
    return render(request, "homepage.html", context)


# Dashboard
@login_required
def dashboard(request):

    user = request.user

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return render(request, "core/dashboard.html")

    address = f"{profile.address_line1}, {profile.city}, {profile.state} {profile.zipcode}"

    print("ADDRESS:", address)

    reps = get_representatives_from_address(address)
    print("REPS:", reps)

    if reps:
        for rep in reps:
            rep_obj, created = Representative.objects.update_or_create(
                Bioguide_id=rep["bioguide_id"],  # ✅ FIXED
                defaults={
                    "name": rep["name"],
                    "district_number": rep["district_number"],
                    "first_name": rep["first_name"],
                    "last_name": rep["last_name"],
                    "state": profile.state,
                    "party": rep["party"],
                    "photo_url": rep["photo_url"],
                }
            )

            rep_obj.constituents.add(user)

    return render(request, "core/dashboard.html", {"show_layout": True, "page": "dashboard"})


# About
def about(request):
    context = {
        "show_layout": True,
        "page": "about",
    }
    return render(request, "about.html", context)


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
        "show_layout": False,
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
        "show_layout": False,
        "page": "login"
    })


# Logout
@require_POST
def accountlogout(request):
    logout(request)
    return redirect("homepage")