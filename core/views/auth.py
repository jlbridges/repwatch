from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core.forms import CustomUserRegister, EmailLoginForm
from core.models import Representative

from .reps_helper import clear_user_reps


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

            if user:
                clear_user_reps(user)

                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
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
    logout(request)

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
