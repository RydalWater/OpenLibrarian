from django.urls import path
from . import views

app_name = 'archives'

urlpatterns = [
    # About Page
    path('', views.about, name='about'),
]