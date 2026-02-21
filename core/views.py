from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

# Homepage
def homepage(request):
    context = {
        "show_layout": True,
        "page": "homepage"
    }
    return render(request, "homepage.html", context) 

# dashboard -- for testing authentication
# @login_required
def dashboard(request):
    context = {
        "show_layout": True,
        "page": "dashboard"
    }
    return render(request, "dashboard.html", context) 

# registration form
def registration(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect("/")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {
        "form": form,
        "show_layout": False # hide navbar and footer
        })

def login_view(request):
    return render(request, "login.html", {"show_layout": False }) # hide navbar and footer


def about(request):
    context = {
        "show_layout": True,
        "page": "about",
    }
    return render(request, "about.html", context)
 
