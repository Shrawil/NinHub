from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat_list, name="chat_list"),
    path("chat/<str:username>/", views.chat, name="chat"),
    path('chat/<str:username>/poll/', views.poll_messages, name='poll_messages'),
    path("<str:username>/followers/", views.followers_view, name="followers_view"),
    path("<str:username>/following/", views.following_view, name="following_view"),
    path("chat/unsend/<int:message_id>/", views.unsend_message, name="unsend_message"),
]