from django.urls import path
from . import views

app_name = 'transfers'
urlpatterns = [
    # Transfers page
    path('', views.transfers, name='transfers'),

    # Social
    path('social-clone/', views.social_clone, name='social_clone'),

    # Profile
    path('profile-clone/', views.profile_clone, name='profile_clone'),

    # List Clone
    path('list-clone/', views.list_clone, name='list_clone'),
    path('gr-clone/', views.goodreads_clone, name='goodreads_clone')

]