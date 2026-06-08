from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import timedelta

from .models import URL

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class URLForm(forms.ModelForm):
    custom_short_code = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Custom code (optional)",
                "pattern": "[a-zA-Z0-9\\-_]+",
                "title": "Only letters, numbers, hyphens, and underscores",
                "class": "form-control",
                "id": "id_custom_short_code",
            }
        ),
    )

    class Meta:
        model = URL
        fields = ["original_url"]
        widgets = {
            "original_url": forms.URLInput(
                attrs={
                    "placeholder": "https://long-url.com/goes/here",
                    "class": "form-control form-control-lg",
                    "autofocus": True,
                }
            ),
        }

    def clean_custom_short_code(self):
        code = self.cleaned_data.get("custom_short_code", "").strip()

        if not code:
            return code

        if len(code) < 3:
            raise forms.ValidationError("Custom code must be at least 3 characters.")

        qs = URL.objects.filter(short_code=code)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"'{code}' is already taken. Try again.")
        return code
