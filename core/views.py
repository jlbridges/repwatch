from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CustomUserRegister, EmailLoginForm, User
from .services.geocodio_service import get_representatives_from_address
from core.services.congress_service import get_member_details
from core.services.bill_service import get_bill_headers
from .models import Representative, Profile, rep_detail, BillHeader


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

# add in code to pass  


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


def clear_user_reps(user):
    reps = Representative.objects.filter(constituents=user)

    for rep in reps:
        rep.constituents.remove(user)

        # delete rep if no users remain
        if rep.constituents.count() == 0:
            rep.delete()

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


# Richard Functions for changing user settings
def updateProfileData(profile, request):    
    if request.POST.get("address_line1"):        
        profile.address_line1 = request.POST.get('address_line1')

    if request.POST.get('address_line2'):
        profile.address_line2 = request.POST.get('address_line2')

    if request.POST.get('city'):
        profile.city = request.POST.get('city')

    if request.POST.get('state'):      
       profile.state = 'NC'

    if request.POST.get('zipcode'):       
        profile.zipcode = request.POST.get('zipcode')

    profile.save()

def updateUserData (postedUser, request):
    if request.POST.get('first_name'):        
        postedUser.first_name = request.POST.get('first_name').strip()

    if request.POST.get('last_name'):
        postedUser.last_name =  request.POST.get('last_name').strip()  

    if request.POST.get('email'):       
        postedUser.email = request.POST.get('email').strip()

    postedUser.save()  
  


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


# Richard functions for checking if user has made changes to profile or account settings. 
# This is used to determine whether to update the database or not, 
# and to prevent unnecessary database writes when no changes have been made.
def check_Profile_changed(request):
        hasValue = False       
        if request.POST.get("address_line1"):
            hasValue - True

        if request.POST.get('address_line2'):
            hasValue = True

        if request.POST.get('city'):
            hasValue = True

        if request.POST.get('state'):
            hasValue = True

        if request.POST.get('zipecode'):
            hasValue = True 

        return hasValue

def check_Account_changed(request):
        hasChanged = False
        if request.POST.get('first_name'):
            hasChanged = True

        if request.POST.get('last_name'):
            hasChanged = True

        if request.POST.get('email'):
            hasChanged =  True
            
        return hasChanged

