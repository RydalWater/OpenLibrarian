from django.urls import path
from . import views

app_name = 'library_card'
urlpatterns = [
    # Library Card Index page
    path('<str:npub>/', views.library_card, name='library_card'),

    # Library Card Data Fetch
    path('card-data/<str:npub>', views.card_data, name='card_data'),

    # Libary Card Explore Profile
    path('explore-profile/<str:npub>', views.explore_profile, name='explore_profile'), 
]