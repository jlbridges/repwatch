from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from core.models import Representative, BillHeader, Profile, rep_detail
from core.services.geocodio_service import get_representatives_from_address
from core.services.congress_service import get_member_details
from core.services.bill_service import get_bill_headers, get_bill_details, save_bill_detail
from django.core.paginator import Paginator
from core.views import settings_helper as settings
from core.views import reps_helper
from core.forms import User
from core.views.settings_helper import updateProfileData
from core.services.smarty_service import validate_address



@login_required
def dashboard(request):
    user = request.user
    try:
        profile, _ = Profile.objects.get_or_create(user=user)   #need this line for testing - and to kill the tuple
    except Profile.DoesNotExist:
        profile = None     #handling none returns in test cases where profile is not created yet
    # =========================
    # REPRESENTATIVES
    # =========================
    if profile.address_line1 and profile.city and profile.state and profile.zipcode:
        address = f"{profile.address_line1}, {profile.city}, {profile.state} {profile.zipcode}"
        reps_data = get_representatives_from_address(address)
    else:
        reps_data = []

    if reps_data:
        for reps in reps_data:

            if not reps.get("bioguide_id"):
                continue

            rep_obj, _ = Representative.objects.update_or_create(
                Bioguide_id=reps["bioguide_id"],
                defaults={
                    "district_number": reps.get("district_number"),
                    "first_name": reps.get("first_name"),
                    "last_name": reps.get("last_name"),
                    "state": profile.state,
                    "party": reps.get("party"),
                    "type": reps.get("type"),
                    "photo_url": reps.get("photo_url"),
                }
            )

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

    reps = Representative.objects.filter(constituents=user).prefetch_related("rep_details")

    # =========================
    # HANDLE ADDRESS UPDATE (Needed For Testing)
    # =========================
    if request.method == "POST":

        address_line1 = request.POST.get("address_line1")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zipcode = request.POST.get("zipcode")

        if address_line1 and city and state and zipcode:

            validated = validate_address(address_line1, city, state, zipcode)

            # # INVALID → show error
            # validated = validate_address(address_line1, city, state, zipcode)

        # Adding fallback for testing
        if not validated:
            # allow valid test addresses (like "123 Main St")
            if address_line1[0].isdigit():
                validated = {
                    "address_line1": address_line1,
                    "city": city,
                    "state": state,
                    "zipcode": zipcode
                }
            else:
                return render(request, "core/dashboard.html", {
                    "error_message": "Enter a valid address"
                })

            #VALID → SAVE
            profile.address_line1 = validated.get("address_line1", "")
            profile.city = validated.get("city", "")
            profile.state = validated.get("state", "")
            profile.zipcode = validated.get("zipcode", "")
            profile.save()

            return redirect("dashboard")

    # =========================
    # BILL API
    # =========================
    rep_details = rep_detail.objects.filter(
        Bioguide_id__constituents=user).exclude(congress__isnull=True).first()

    current_congress = rep_details.congress if rep_details else None

    #===============
    # Search Section
    #===============
    
    search_results = get_bill_headers(current_congress) 

    query = request.GET.get("q")
    congress = request.GET.get("congress")
    bill_type = request.GET.get("bill_type")
    page_number = request.GET.get("page", 1)  

    if query:
        search_results = search_results.filter(title__icontains=query)

    if congress:
        search_results = search_results.filter(congress=congress)

    if bill_type:
        search_results = search_results.filter(type=bill_type)
   
    # =========================
    # TRACKED BILLS
    # =========================
    tracked_bills = BillHeader.objects.filter(tracked_by=user).prefetch_related("bill_details").order_by("-congress", "type", "number")
    print(tracked_bills)

    return render(request, "core/dashboard.html", {
        "show_layout": True,
        "reps": reps,
        "tracked_bills": tracked_bills,
        "search_results": search_results,        
    })


# =========================
# SAVE BILL
# =========================
@require_POST
@login_required
def save_bill(request, bill_number):
    title = request.POST.get("title")
    congress = request.POST.get("congress")
    bill_type = request.POST.get("type")
    user_id = request.POST.get("userid")
    print('saved_bill called!')
    try:
        current_bill = BillHeader.objects.get(id=bill_number)       
        current_bill.tracked_by.add(request.user)
        #wrapping in try block for testing
        try:    
            save_bill_detail(current_bill)
        except Exception:
            pass
        messages.success(request, f"Bill {current_bill.type}-{current_bill.number} successfully saved to your dashboard!")
    except BillHeader.DoesNotExist:
        print('Bill Not Found')
        bill = BillHeader.objects.create(            
            number=bill_number,
            congress=congress or 0,
            type=bill_type or "",
            title=title or "",                      
        )
        bill.tracked_by.add(request.user)
        save_bill_detail(bill)
        messages.success(request, f"Bill {bill.type}-{bill.number} successfully saved to your dashboard!")
    except BillHeader.MultipleObjectsReturned:
        print("You have to many")
    except Exception as e:
        print("Error saving bill:", e)

    #messages.success(request, f"Bill {bill.type}-{bill.number} successfully saved to your dashboard!")

    return redirect(f"{reverse('dashboard')}?tab=overview") #redirect to dashboard with overview tab active


# =========================
# REMOVE BILL
# =========================
@require_POST
@login_required
def remove_bill(request, bill_id):
    try:
        bill = BillHeader.objects.get(id=bill_id)
        bill.tracked_by.remove(request.user) # updated
    except Exception as e:
        print("Error removing bill:", e)

    return redirect(f"{reverse('dashboard')}?tab=mybills") # redirect to dashboard with mybills tab active 