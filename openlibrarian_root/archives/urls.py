from django.urls import path
from . import views

app_name = "archives"

urlpatterns = [
    # About Page
    path("", views.about, name="about"),
    # Updates & Features
    path("updates/", views.updates, name="updates"),
    # Privacy Policy
    path("privacy/", views.privacy, name="privacy"),
]
