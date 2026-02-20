from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from .views import dashboard, registration, login_view, homepage, about

urlpatterns = [
    path("", homepage, name="homepage"),
    path("accounts/login/", login_view, name="login"),
    path("accounts/signup/", registration, name="registration"),
    path("dashboard/", dashboard, name="dashboard"),
    path("about/", about, name="about"),
    path ("logout/", auth_views.LogoutView.as_view(next_page=reverse_lazy('homepage')), name="logout" ) 
]
