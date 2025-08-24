from django.urls import path
from . import views

app_name = "almanac"
urlpatterns = [
    # Settings page
    path("", views.user_settings, name="settings"),
    # User profile view
    path("profile/", views.user_profile, name="user_profile"),
    # User relays view
    path("relays/", views.user_relays, name="user_relays"),
    # Following
    path("friends/", views.user_friends, name="user_friends"),
]
