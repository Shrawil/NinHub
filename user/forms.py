from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UsernameField


class ProfileForm(forms.ModelForm):
    # Custom username field so users can edit their username
    # alongside their profile information.
    username = UsernameField(
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Enter new username"
        })
    )

    class Meta:
        model = Profile

        # Profile fields plus the custom username field.
        fields = ["username", "pfp", "bio", "website", "location"]

        # Customize the appearance of form inputs.
        widgets = {
            "pfp": forms.FileInput(attrs={
                "id": "id_pfp",
                "hidden": True,
                "accept": "image/*",
            }),
            "bio": forms.Textarea(attrs={
                "rows": 4,
                "class": "form-input"
            }),
            "website": forms.URLInput(attrs={
                "class": "form-input",
                "placeholder": "https://example.com"
            }),
            "location": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Your location"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fill the username field with the current username.
        self.fields["username"].initial = self.instance.user.username

    def clean_username(self):
        username = self.cleaned_data["username"]

        # Ensure no other user already has this username.
        if User.objects.exclude(
            pk=self.instance.user.pk
        ).filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def save(self, commit=True):
        # Save the profile without committing yet,
        # so the linked User model can be updated first.
        profile = super().save(commit=False)

        # Update the associated User object's username.
        profile.user.username = self.cleaned_data["username"]

        if commit:
            profile.user.save()
            profile.save()

        return profile


# Uses Django's built-in registration form without modifications.
class RegisterForm(UserCreationForm):
    pass