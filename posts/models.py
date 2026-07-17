from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Post(models.Model):
    # Each post belongs to one user.
    # If the user is deleted, all their posts are deleted as well.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"  # Allows: user.posts.all()
    )

    # Stores uploaded images inside MEDIA_ROOT/posts/
    # Only allows the specified image file extensions.
    image = models.ImageField(
        upload_to="posts/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"]
            )
        ]
    )

    caption = models.TextField(blank=True)

    # Automatically stores the timestamp when the post is first created.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Human-readable representation shown in Django admin and shell.
        return f"{self.user.username} - {self.id}"

    def is_liked_by(self, user):
        # Returns True if the given user has liked this post.
        return self.likes.filter(user=user).exists()


class Like(models.Model):
    # User who liked the post.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    # Post that received the like.
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"  # Allows: post.likes.all()
    )

    class Meta:
        # Prevents the same user from liking the same post more than once.
        unique_together = ("user", "post")


class Comment(models.Model):
    # User who wrote the comment.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    # Post on which the comment was made.
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"  # Allows: post.comments.all()
    )

    text = models.TextField()

    # Automatically stores when the comment was created.
    created_at = models.DateTimeField(auto_now_add=True)