from django.shortcuts import render


# About
def about(request):
    return render(request, "about.html", {
        "show_layout": True,
        "page": "about",
    })
