from django.db.models import Exists, OuterRef
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PostForm, CommentForm
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Like
from django.shortcuts import redirect


# Allows logged-in users to add a comment to a specific post.
@login_required
def add_comment(request, post_id):
    # Fetch the post or return a 404 page if it doesn't exist.
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            # Create the comment object without saving yet,
            # so we can assign the user and post first.
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()

    return redirect('post_detail', post_id=post.id)


# Toggles like/unlike for the current user.
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Creates a like if it doesn't exist, otherwise returns the existing one.
    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        # User already liked the post, so remove the like.
        like.delete()
        liked = False
    else:
        liked = True

    # Return updated like status and total likes for AJAX requests.
    return JsonResponse({
        "liked": liked,
        "likes": post.likes.count()
    })


# Handles creation of new posts.
@login_required
def create_post(request):
    if request.method == "POST":
        # request.FILES is required to handle uploaded images.
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            # Assign the logged-in user before saving.
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            return redirect("home")
    else:
        form = PostForm()

    return render(request, "posts/create.html", {
        "form": form
    })


# Displays a single post along with its comments and like status.
@login_required
def post_detail(request, post_id):

    # Subquery that checks whether the current user has liked this post.
    liked = Like.objects.filter(
        user=request.user,
        post=OuterRef("pk")
    )

    # Annotate the post with a boolean field: is_liked.
    post = get_object_or_404(
        Post.objects.annotate(
            is_liked=Exists(liked)
        ),
        pk=post_id
    )

    return render(request, "posts/detail.html", {
        "post": post,
        "comment_form": CommentForm(),
    })


# Displays a list of users who liked a post.
def like_list(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Retrieve all likes associated with this post.
    likes = Like.objects.filter(post=post)

    return render(request, "posts/like_list.html", {
        "post": post,
        "likes": likes,
    })