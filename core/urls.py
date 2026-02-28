from django.urls import path
from .views import homepage, dashboard, about

urlpatterns = [
    path("", homepage, name="homepage"),
    path("dashboard/", dashboard, name="dashboard"),
    path("about/", about, name="about"),
]
