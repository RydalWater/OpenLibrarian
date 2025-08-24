from django.urls import path
from . import views

app_name = "library"
urlpatterns = [
    # Library Index page
    path("", views.library, name="library"),
    # Shelves page
    path("shelves/", views.library_shelves, name="library_shelves"),
    # Review page
    path("reviews/", views.reviews, name="reviews"),
]
