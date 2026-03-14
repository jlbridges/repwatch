from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy

from .views import homepage, dashboard, about, login_view, representative_detail

urlpatterns = [
    path("", homepage, name="homepage"),

    path("dashboard/", dashboard, name="dashboard"),

    path("about/", about, name="about"),

    path("login/", login_view, name="login"),

    path(
        "representatives/<str:bioguide_id>/",
        login_required(representative_detail),
        name="rep_detail",
    ),

    path(
        "password/change/",
        login_required(
            auth_views.PasswordChangeView.as_view(
                template_name="registration/pwChangeForm.html",
                success_url=reverse_lazy("passwordChangeDone"),
            )
        ),
        name="passwordChange",
    ),

    path(
        "password/change/done/",
        login_required(
            auth_views.PasswordChangeDoneView.as_view(
                template_name="registration/pwChangeDone.html",
            )
        ),
        name="passwordChangeDone",
    ),
]