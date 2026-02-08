from django.urls import path
from .views import dashboard, register

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("register/", register, name="register"),
]