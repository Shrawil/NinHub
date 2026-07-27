from django.db import models
from user.models import User


class Follow(models.Model):
    # The user being followed.
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'  # Allows: user.follower.all()
    )

    # The user who follows someone.
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'  # Allows: user.following.all()
    )

    # Timestamp when the follow relationship was created.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent a user from following the same person more than once.
        unique_together = ('following', 'follower')

    def __str__(self):
        # Human-readable representation shown in Django admin and shell.
        return f"{self.follower} -> {self.following}"


class Message(models.Model):
    # User who sent the message.
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    # User who received the message.
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )

    text = models.TextField(max_length=1000)

    # Automatically stores when the message was sent.
    created_at = models.DateTimeField(auto_now_add=True)

    # Tracks whether the receiver has opened/read the message.
    is_read = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        # Display messages in chronological order by default.
        ordering = ["created_at"]


class Notification(models.Model):
    # User who will receive the notification.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    # User who triggered the notification.
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )

    text = models.CharField(max_length=255)

    # Tracks whether the notification has been viewed.
    is_read = models.BooleanField(default=False)

    # Automatically stores when the notification was created.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Show newest notifications first.
        ordering = ["-created_at"]