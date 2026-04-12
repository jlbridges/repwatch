from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from core.models import Representative, Profile, BillHeader
from core.services.geocodio_service import get_representatives_from_address
from core.services.congress_service import get_member_details
from core.services.bill_service import get_bill_headers


@login_required
def dashboard(request):
    user = request.user

    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        profile.address_line1 = request.POST.get("address_line1", "")
        profile.address_line2 = request.POST.get("address_line2", "")
        profile.city = request.POST.get("city", "")
        profile.state = request.POST.get("state", "")
        profile.zipcode = request.POST.get("zipcode", "")
        profile.save()

    # =========================
    # BILL API
    # =========================
    current_congress = 118
    get_bill_headers(current_congress)

    # =========================
    # SEARCH
    # =========================
    query = request.GET.get("q")
    congress = request.GET.get("congress")
    bill_type = request.GET.get("bill_type")

    search_results = BillHeader.objects.all()

    if query:
        search_results = search_results.filter(title__icontains=query)

    if congress:
        search_results = search_results.filter(congress=congress)

    if bill_type:
        search_results = search_results.filter(type=bill_type)

    # =========================
    # REPRESENTATIVES
    # =========================
    address = f"{profile.address_line1}, {profile.city}, {profile.state} {profile.zipcode}"

    reps_data = get_representatives_from_address(address)

    if reps_data:
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

            try:
                member_details = get_member_details(rep["bioguide_id"])
            except Exception:
                member_details = {}

            rep_obj.constituents.add(user)

    reps = Representative.objects.filter(constituents=user).prefetch_related("rep_details")

    # =========================
    # TRACKED BILLS
    # =========================
    tracked_bills = BillHeader.objects.filter(saved_by=user)

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

    try:
        bill, created = BillHeader.objects.get_or_create(
            number=bill_number,
            congress=congress,
            type=bill_type,
            defaults={"title": title}
        )

        bill.saved_by.add(request.user)

    except Exception as e:
        print("Error saving bill:", e)

    return redirect("dashboard")


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

    return redirect("dashboard")