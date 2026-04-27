from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.models import BillHeader

@login_required
def tracked_bills_json(request):
    user = request.user
    bills = BillHeader.objects.filter(saved_by=user)\
        .prefetch_related("bill_details").order_by("-congress", "type", "number")

    payload = []
    for bill in bills:
        detail = bill.bill_details.first()
        payload.append({
            "id": bill.id,
            "type": bill.type,
            "number": bill.number,
            "title": bill.title,
            "congress": bill.congress,
            "originChamberCode": bill.originChamberCode,
            "detail": {
                "bill_status": detail.bill_status if detail else None,
                "introducedDate": detail.introducedDate.isoformat() if detail and detail.introducedDate else None,
                "bill_summary": detail.bill_summary if detail else None,
                "actionDesc": detail.actionDesc if detail else None,
            } if detail else None,
        })

    return JsonResponse({"bills": payload})