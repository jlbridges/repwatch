# core/forms.py

from django import forms
import re


ADDRESS_REGEX = re.compile(
    r"^\d+\s+[A-Za-z0-9\s\.]+,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}$"
)


class CustomSignupForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=150)
    address = forms.CharField(max_length=255)

    def clean_address(self):
        address = self.cleaned_data.get("address", "")

        if not ADDRESS_REGEX.match(address):
            raise forms.ValidationError("Enter a valid address")

        return address

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned