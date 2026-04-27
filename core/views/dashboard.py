from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from core.models import Representative, BillHeader, Profile, rep_detail
from core.services.geocodio_service import get_representatives_from_address
from core.services.congress_service import get_member_details
from core.services.bill_service import (
    get_bill_headers,
    get_bill_header_data,
    save_bill_for_user,
    remove_bill_for_user,
    DuplicateBillError,
)
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
    # SEARCH
    # =========================
    search_results = get_bill_header_data(user)
   
    return render(request, "core/dashboard.html", {
        "show_layout": True,
        "reps": reps,
        "search_results": search_results,
    })


# =========================
# SAVE BILL
# =========================
@require_POST
@login_required
def save_bill(request, bill_number):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    try:
        bill, _ = save_bill_for_user(
            request.user,
            number=bill_number,
            congress=request.POST.get("congress"),
            bill_type=request.POST.get("type"),
            title=request.POST.get("title"),
        )
    except DuplicateBillError as e:
        print(e)
        if is_ajax:
            return JsonResponse(
                {"ok": False, "error": "Duplicate bill records exist. Please contact support."},
                status=500,
            )
        return redirect(f"{reverse('dashboard')}?tab=overview")
    except Exception as e:
        print("Error saving bill:", e)
        if is_ajax:
            return JsonResponse({"ok": False, "error": "Failed to save bill."}, status=500)
        return redirect(f"{reverse('dashboard')}?tab=overview")

    if is_ajax:
        return JsonResponse({
            "ok": True,
            "id": bill.id,
            "message": f"Bill {bill.type}. {bill.number} saved to your dashboard!",
        })
    messages.success(request, f"Bill {bill.type}-{bill.number} successfully saved to your dashboard!")
    return redirect(f"{reverse('dashboard')}?tab=overview")


# =========================
# REMOVE BILL
# =========================
@require_POST
@login_required
def remove_bill(request, bill_id):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    try:
        bill = remove_bill_for_user(request.user, bill_id)
        if is_ajax:
            return JsonResponse({
                "ok": True,
                "message": f"Bill {bill.type}. {bill.number} removed from your dashboard.",
            })
    except Exception as e:
        print("Error removing bill:", e)
        if is_ajax:
            return JsonResponse({"ok": False, "error": "Failed to remove bill."}, status=500)

    return redirect(f"{reverse('dashboard')}?tab=mybills") # redirect to dashboard with mybills tab active