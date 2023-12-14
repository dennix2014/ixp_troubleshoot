"""ixpn_dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.dashboard, name='dashboard')
Class-based views
    1. Add an import:  from other_app.views import dashboard
    2. Add a URL to urlpatterns:  path('', dashboard.as_view(), name='dashboard')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from ixp_troubleshoot.local_settings import admin_url
from tshoot.views import home

urlpatterns = [
    path('', home, name='home'),
    path(admin_url, admin.site.urls),
    path('tshoot/', include('tshoot.urls')),
    path('accounts/', include('allauth.urls')),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
