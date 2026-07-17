from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Profile(models.Model):
    # Each user has exactly one profile.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"  # Allows: user.profile
    )

    # Stores profile pictures in MEDIA_ROOT/profile_pictures/.
    # Uses a default image if the user hasn't uploaded one.
    pfp = models.ImageField(
        upload_to="profile_pictures/",
        default="profile_pictures/default.png",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"]
            )
        ],
    )

    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    # Automatically stores when the profile was created.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Human-readable representation shown in Django admin and shell.
        return self.user.username