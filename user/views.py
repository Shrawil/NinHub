from social.models import Follow
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from .forms import ProfileForm
from user.models import Profile
from posts.models import Post, Like
from posts.forms import CommentForm
from django.db.models import Exists, OuterRef, Count


# Handles new user registration.
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


# Handles user login.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Verify the provided credentials.
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(
                request,
                'accounts/login.html',
                {'error': 'Invalid Credentials!'}
            )

    return render(request, 'accounts/login.html')


# Logs the user out and redirects to the login page.
def logout_view(request):
    logout(request)
    return redirect('login')


# Displays the home feed.
@login_required
def home_view(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    # Subquery used to determine whether the current user
    # has liked each post.
    liked_posts = Like.objects.filter(
        user=request.user,
        post=OuterRef("pk")
    )

    # Show posts from other users and annotate each one
    # with an 'is_liked' boolean.
    posts = (
        Post.objects
        .exclude(user=request.user)
        .annotate(is_liked=Exists(liked_posts))
        .order_by("is_liked", "-created_at")
    )

    # IDs of users the current user already follows.
    already_following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list("following_id", flat=True)

    # Suggest popular users that the current user isn't following.
    suggested_users = (
        User.objects.exclude(id=request.user.id)
        .exclude(id__in=already_following_ids)
        .annotate(follower_count=Count("follower"))
        .order_by("-follower_count")[:5]
    )

    return render(request, "user/home.html", {
        "posts": posts,
        "liked_posts": liked_posts,
        "profile": profile,
        "comment_form": CommentForm(),
        "suggested_users": suggested_users,
    })


# Displays the logged-in user's own profile.
@login_required
def profile_view(request):
    profile = request.user.profile

    return render(request, 'user/profile.html', {
        'profile': profile,
        'is_me': True
    })


# Allows users to delete only their own posts.
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Prevent deleting someone else's post.
    if post.user != request.user:
        return redirect("me")

    if request.method == "POST":
        post.delete()

    return redirect("me")


# Allows users to edit their profile information.
@login_required
def edit_view(request):
    profile = request.user.profile

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect("me")

    else:
        form = ProfileForm(instance=profile)

    return render(request, "user/edit.html", {
        "form": form
    })


# Displays another user's profile.
@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)

    # Used by the template to determine whether to show
    # Edit Profile or Follow/Unfollow buttons.
    is_me = (request.user == user)

    # Check if the current user already follows this profile.
    is_following = Follow.objects.filter(
        follower=request.user,
        following=user
    ).exists()

    return render(request, "user/profile.html", {
        'profile': user.profile,
        'is_me': is_me,
        'is_following': is_following
    })


# Creates a follow relationship.
@login_required
def follow_user(request, username):
    # Only allow follow requests via POST.
    if request.method != "POST":
        return redirect("user_profile", username=username)

    user = get_object_or_404(User, username=username)

    # Prevent users from following themselves.
    if request.user != user:
        Follow.objects.get_or_create(
            follower=request.user,
            following=user,
        )

    # Redirect back to the page where the follow request originated.
    next_page = request.GET.get("next")

    if next_page == "home":
        return redirect("home")

    return redirect("user_profile", username=username)


# Removes a follow relationship.
@login_required
def unfollow_user(request, username):
    # Only allow unfollow requests via POST.
    if request.method != "POST":
        return redirect("user_profile", username=username)

    user = get_object_or_404(User, username=username)

    Follow.objects.filter(
        follower=request.user,
        following=user
    ).delete()

    return redirect("user_profile", username=username)


# Search users by username.
@login_required
def search_view(request):
    query = request.GET.get("q", "")

    # Return an empty queryset when no search term is entered.
    users = User.objects.none()

    if query:
        users = User.objects.filter(
            username__icontains=query
        )

    return render(request, "user/search.html", {
        "query": query,
        "users": users,
    })