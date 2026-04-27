# core/forms.py
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
import re

from core.services.smarty_service import validate_address
from .models import Profile

User = get_user_model()


class CustomUserRegister(UserCreationForm):

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    address_line1 = forms.CharField(required=True)
    address_line2 = forms.CharField(required=False)
    city = forms.CharField(required=True)

    STATE_CHOICES = (
        ("", "Select your state"),
        ("NC", "NC"),
    )

    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        initial="",
    )

    zipcode = forms.CharField(required=True, max_length=10)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    # ------------------------------
    # Field Validations
    # ------------------------------

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_state(self):
        state = self.cleaned_data["state"]

        if state != "NC":
            raise forms.ValidationError("Only NC is allowed.")

        return state

    def clean_zipcode(self):
        zipcode = self.cleaned_data["zipcode"].strip()

        if not re.match(r'^\d{5}(-\d{4})?$', zipcode):
            raise forms.ValidationError(
                "Enter a valid 5-digit ZIP code."
            )

        return zipcode

    # ------------------------------
    # Smarty Address Validation
    # ------------------------------

    def clean(self):

        cleaned = super().clean()

        address = cleaned.get("address_line1")
        city = cleaned.get("city")
        state = cleaned.get("state")
        zipcode = cleaned.get("zipcode")

        if address and city and state and zipcode:

            validated = validate_address(
                address,
                city,
                state,
                zipcode
            )

            # Reject fake addresses
            if not validated:
                raise forms.ValidationError(
                    "Address could not be validated. Please enter a real address."
                )

            # Replace user input with standardized address
            cleaned["address_line1"] = validated["address_line1"]
            cleaned["city"] = validated["city"]
            cleaned["state"] = validated["state"]
            cleaned["zipcode"] = validated["zipcode"]

        return cleaned

    # ------------------------------
    # Save User + Profile
    # ------------------------------

    @transaction.atomic
    def save(self, commit=True):

        user = super().save(commit=False)

        email = self.cleaned_data["email"]

        user.username = email
        user.email = email
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:

            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)

            profile.address_line1 = self.cleaned_data["address_line1"]
            profile.address_line2 = self.cleaned_data.get(
                "address_line2", ""
            )
            profile.city = self.cleaned_data["city"]
            profile.state = self.cleaned_data["state"]
            profile.zipcode = self.cleaned_data["zipcode"]

            profile.save()

        return user


class EmailLoginForm(forms.Form):

    email = forms.EmailField(required=True)

    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True
    )

    def clean(self):

        cleaned = super().clean()

        email = (cleaned.get("email") or "").strip().lower()
        password = cleaned.get("password")

        if email and password:

            user = authenticate(
                username=email,
                password=password
            )

            if user is None:
                raise forms.ValidationError(
                    "Invalid email or password."
                )

            self.user = user

        return cleaned


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