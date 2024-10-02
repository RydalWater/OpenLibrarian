"""
URL configuration for openlibrarian project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Langing pages and login/logout
    path('', include('circulation_desk.urls')),
    # User profile
    path('almanac/', include('almanac.urls')),
    # Glossary
    path('glossary/', include('glossary.urls')),
    # Library
    path('library/', include('library.urls')),
    # Library Card
    path('card/', include('library_card.urls')),
    # Archives
    path('archives/', include('archives.urls')),
    # Transfers
    path('transfers/', include('transfers.urls')),
]

handler404 = "archives.views.page_not_found_view"