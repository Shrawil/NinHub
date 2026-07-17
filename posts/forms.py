from django import forms
from .models import Post
from .models import Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        # Only expose these fields in the form.
        fields = ["image", "caption"]

        # Customize the default form inputs.
        widgets = {
            # Accept only image files in the file picker.
            "image": forms.ClearableFileInput(
                attrs={
                    "id": "id_image",
                    "accept": "image/*"
                }
            ),

            # Add placeholder text to the caption field.
            "caption": forms.Textarea(
                attrs={
                    "placeholder": "Write a caption..."
                }
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        # Users only need to enter the comment text.
        fields = ["text"]

        # Customize the comment input field.
        widgets = {
            "text": forms.TextInput(
                attrs={
                    "placeholder": "Add a comment...",
                    "autocomplete": "off",  # Prevent browser autocomplete suggestions.
                }
            )
        }