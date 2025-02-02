from django.urls import path
from . import views

app_name = 'circulation_desk'
urlpatterns = [
    # Home/index Page for site
    path('', views.index, name='index'),

    # Login Pages
    path('login/', views.login_view, name='login'),
    path('login-npub/', views.login_npub_view, name='login-npub'),
    path('login-nsec/', views.login_nsec_view, name='login-nsec'),
    path('login-seed/', views.login_seed_view, name='login-seed'),
    path('login-nip07/', views.login_nip07_view, name='login-nip07'),

    # Logout Page
    path('logout/', views.logout_view, name='logout'),

    # Registration Pages
    path('create-account/', views.create_account_view, name='create-account'),
    path('create-account-confirm/', views.create_account_confirm_view, name='create-account-confirm'),

    # Json Responses
    path('event_publisher/', views.event_publisher, name='event_publisher'),
    path('fetch_events/', views.fetch_events, name='fetch_events'),
    path('create_account_empty/', views.create_account_empty, name='create_account_empty'),
    
]