# core/forms.py
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Profile

User = get_user_model()


class CustomUserRegister(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    address = forms.CharField(required=False)
    city = forms.CharField(required=False)

    STATE_CHOICES = (
        ("", "Select your state"), # placeholder
        ("NC", "NC"),
        )
    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="State",
    )

    zip_code = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_state(self):
        state = self.cleaned_data["state"]
        if state != "NC":
            raise forms.ValidationError("Only NC is allowed.")
        return state

    def save(self, commit=True):
        user = super().save(commit=False)

        email = self.cleaned_data["email"].strip().lower()
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.address = self.cleaned_data.get("address", "") or ""
            profile.city = self.cleaned_data.get("city", "") or ""
            profile.state = self.cleaned_data.get("state", "NC")
            profile.zip_code = self.cleaned_data.get("zip_code", "") or ""
            profile.save()

        return user


class EmailLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned = super().clean()
        email = (cleaned.get("email") or "").strip().lower()
        password = cleaned.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
            self.user = user

        return cleaned


# For django-allauth: this is what ACCOUNT_SIGNUP_FORM_CLASS points to.
# allauth requires a plain forms.Form with a signup(self, request, user) method. [web:87]
class CustomSignupForm(forms.Form):
    state = forms.ChoiceField(
        choices=(("NC", "NC"),),
        initial="NC",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="State",
    )

    def signup(self, request, user):
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.state = self.cleaned_data["state"]
        profile.save()
