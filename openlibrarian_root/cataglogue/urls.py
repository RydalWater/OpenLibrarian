from django.urls import path
from . import views

app_name = 'cataglogue'
urlpatterns = [
    # Cataglogue Index page
    path('', views.cataglogue, name='cataglogue'),

    # Search page
    path('search/', views.search, name='search'),

    # Interest page
    path('interests/', views.interests, name='interests'),
]