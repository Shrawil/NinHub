from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UsernameField


class ProfileForm(forms.ModelForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Enter new username"
        })
    )

    class Meta:
        model = Profile
        fields = ["username", "pfp", "bio", "website", "location"]

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

        # Show current username
        self.fields["username"].initial = self.instance.user.username

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.exclude(pk=self.instance.user.pk).filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")

        return username

    def save(self, commit=True):
        profile = super().save(commit=False)

        profile.user.username = self.cleaned_data["username"]

        if commit:
            profile.user.save()
            profile.save()

        return profile
    
class RegisterForm(UserCreationForm):
    pass