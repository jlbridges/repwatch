from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import CustomUserRegister, EmailLoginForm

# Homepage
def homepage(request):
    context = {
        "show_layout": True,
        "page": "homepage"
    }
    return render(request, "homepage.html", context) 

# dashboard -- for testing authentication
@login_required
def dashboard(request):
    context = {
        "show_layout": True,
        "page": "dashboard"
    }
    return render(request, "dashboard.html", context) 

# about
def about(request):
    context = {
        "show_layout": True,
        "page": "about",
    }
    return render(request, "about.html", context)

# registration 
def registration(request):
    if request.method == "POST":
        form = CustomUserRegister(request.POST)
        if form.is_valid():
            user = form.save() # save user + creates profile
            return redirect("dashboard")
    else:
        form = CustomUserRegister()

    return render(request, "signup.html", {
        "form": form,
        "show_layout": False, # hide navbar and footer
        "page": "signup",
    })


# Login
def login_view(request):
    if request.method == "POST":
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            # log in the authenticated user
            login(request, form.user)
            return redirect("dashboard")
    else:
        form = EmailLoginForm()

    return render(request, "login.html", {"form": form, "show_layout": False, "page": "login"})  # hide navbar and footer

@login_required
def accountlogout(request):
    # Your base template uses a POST form for logout
    if request.method == "POST":
        logout(request)
    return redirect("homepage")
