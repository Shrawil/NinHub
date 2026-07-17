from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Message, Notification, Follow


# Handles both displaying the chat and sending new messages.
@login_required
def chat(request, username):
    other_user = get_object_or_404(User, username=username)

    if request.method == "POST":
        text = request.POST.get("message", "").strip()

        if text:
            # Save the new message.
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                text=text
            )

            # Keep only one unread notification per sender.
            # If one already exists, update it instead of creating duplicates.
            Notification.objects.update_or_create(
                user=other_user,
                sender=request.user,
                notif_type="message",
                is_read=False,
                defaults={"text": f"New message from {request.user.username}"},
            )

        # Normal form submission redirects back to the chat.
        # AJAX requests receive JSON instead.
        if request.headers.get("X-Requested-With") != "XMLHttpRequest":
            return redirect("chat", username=username)

        return JsonResponse({"status": "ok"})

    # Opening the chat marks incoming messages and notifications as read.
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    Notification.objects.filter(
        user=request.user,
        sender=other_user,
        is_read=False
    ).update(is_read=True)

    # Retrieve all messages exchanged between both users.
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    )

    return render(request, "social/chat.html", {
        "other_user": other_user,
        "messages": messages
    })


# Displays the user's chat inbox with the latest message from each conversation.
@login_required
def chat_list(request):
    # Fetch every message involving the current user, newest first.
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related("sender", "receiver").order_by("-created_at")

    chat_data = []
    seen = {}

    for message in messages:
        # Determine who the conversation is with.
        other_user = (
            message.receiver if message.sender == request.user else message.sender
        )

        # Only keep the latest message for each user.
        if other_user.id not in seen:

            # Count unread messages from this user.
            unread_count = Message.objects.filter(
                sender=other_user,
                receiver=request.user,
                is_read=False
            ).count()

            entry = {
                "user": other_user,
                "last_message": message.text,
                "last_time": message.created_at,
                "unread_count": unread_count,
            }

            seen[other_user.id] = entry
            chat_data.append(entry)

    context = {
        "chat_data": chat_data
    }

    return render(request, "social/chat_list.html", context)


# Returns only messages newer than the given ID.
# Used for live chat updates without refreshing the page.
def poll_messages(request, username):
    other_user = User.objects.get(username=username)

    after_id = request.GET.get('after_id', 0)

    msgs = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user],
        id__gt=after_id,
    ).order_by('id')

    data = [
        {
            'id': m.id,
            'sender': m.sender.username,
            'text': m.text,
            # Indicates whether the message belongs to the current user.
            'is_me': m.sender_id == request.user.id,
        }
        for m in msgs
    ]

    return JsonResponse({'messages': data})


# Displays everyone who follows the selected user.
def followers_view(request, username):
    profile_user = get_object_or_404(User, username=username)

    followers = Follow.objects.filter(
        following=profile_user
    ).select_related("follower")

    # Users that the current logged-in user follows.
    # Used to decide whether to show Follow/Following buttons.
    following_users = User.objects.filter(
        id__in=Follow.objects.filter(
            follower=request.user
        ).values_list("following_id", flat=True)
    )

    return render(request, "social/follow_list.html", {
        "profile_user": profile_user,
        "users": followers,
        "title": "Followers",
        "following_users": following_users,
    })


# Displays everyone the selected user is following.
def following_view(request, username):
    profile_user = get_object_or_404(User, username=username)

    following = Follow.objects.filter(
        follower=profile_user
    ).select_related("following")

    # Users that the current logged-in user follows.
    following_users = User.objects.filter(
        id__in=Follow.objects.filter(
            follower=request.user
        ).values_list("following_id", flat=True)
    )

    return render(request, "social/follow_list.html", {
        "profile_user": profile_user,
        "users": following,
        "title": "Following",
        "following_users": following_users,
    })