from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from core.models import Representative, BillHeader, Profile, rep_detail
from core.services.geocodio_service import get_representatives_from_address, validate_address
from core.services.congress_service import get_member_details
from core.services.bill_service import get_bill_headers, get_bill_details, save_bill_detail
from django.core.paginator import Paginator
from core.views import settings_helper as settings
from core.views import reps_helper
from core.forms import User





@login_required
@login_required
def dashboard(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)     
    except Profile.DoesNotExist:
        profile = None     #handling none returns in test cases where profile is not created yet
    # =========================
    # REPRESENTATIVES
    # =========================
    address = f"{profile.address_line1}, {profile.city}, {profile.state} {profile.zipcode}"

    reps_data = get_representatives_from_address(address)

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
    # BILL API
    # =========================
    rep_details = rep_detail.objects.filter(
        Bioguide_id__constituents=user).exclude(congress__isnull=True).first()

    current_congress = rep_details.congress if rep_details else None
    
    search_results = get_bill_headers(current_congress)   
    # =========================
    # SEARCH
    # =========================
    query = request.GET.get("q")
    congress = request.GET.get("congress")
    bill_type = request.GET.get("bill_type")
    page_number = request.GET.get("page", 1)   
   
    # =========================
    # TRACKED BILLS
    # =========================
    tracked_bills = BillHeader.objects.filter(saved_by=user).prefetch_related("bill_details").order_by("-congress", "type", "number")
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
        current_bill = BillHeader.objects.get(number=bill_number,congress=congress,type=bill_type)       
        current_bill.saved_by.add(request.user)    
        save_bill_detail(current_bill)
        messages.success(request, f"Bill {current_bill.type}-{current_bill.number} successfully saved to your dashboard!")
    except BillHeader.DoesNotExist:
        print('Bill Not Found')
        bill = BillHeader.objects.create(            
            number=bill_number,
            congress=congress,
            type=bill_type,
            title = title,                      
        )              
        bill.saved_by.add(request.user)
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
        bill.saved_by.remove(request.user)
    except Exception as e:
        print("Error removing bill:", e)

    return redirect(f"{reverse('dashboard')}?tab=mybills") # redirect to dashboard with mybills tab active 