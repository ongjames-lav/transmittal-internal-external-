"""
URL configuration for emailsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include, re_path
from django.views.static import serve
from django.views.generic import TemplateView
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('transmittals/', include('transmittals.urls')),
    path('', accounts_views.index_redirect, name='home'),
]

from django.conf import settings
from django.conf.urls.static import static

# Media file patterns
urlpatterns += [
    # Protected media files (require login)
    re_path(r'^media/external_transmittals/(?P<filepath>.*)$', accounts_views.serve_protected_media, name='protected_media'),
    re_path(r'^media/transmittals/(?P<filepath>.*)$', accounts_views.serve_protected_media, name='protected_transmittal_media'),
]

# Unprotected media files (served directly)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

