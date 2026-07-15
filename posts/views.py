from django.db.models import Exists, OuterRef
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PostForm, CommentForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Like
from django.templatetags.static import static

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()


    pfp = (
        request.user.profile.pfp.url
        if request.user.profile.pfp
        else static("images/default.png")
    )

    return JsonResponse({
        "username": request.user.username,
        "comment": comment.text,
        "pfp": pfp,
    })

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        "liked": liked,
        "likes": post.likes.count()
    })

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("home")
    else:
        form = PostForm()
    return render(request, "posts/create.html", {
        "form": form
    })


@login_required
def post_detail(request, post_id):

    liked = Like.objects.filter(
        user=request.user,
        post=OuterRef("pk")
    )

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

def like_list(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    likes = Like.objects.filter(post=post)

    return render(request, "posts/like_list.html", {
        "post": post,
        "likes": likes,
    })