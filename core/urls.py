from django.urls import path
from .views import homepage, dashboard, about, login_view

urlpatterns = [
    path("", homepage, name="homepage"),
    path("dashboard/", dashboard, name="dashboard"),
    path("about/", about, name="about"),
    path("login/", login_view, name="login"), #added code for the correct pathing for the login view
]