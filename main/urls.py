"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path,include 
from main import settings
from django.views.static import serve
from .schema import schema_view
from accounts import views as accounts_view

admin.site.site_header = "Medical Admin"
admin.site.site_title = "Medical Admin Portal"
admin.site.index_title = "Welcome to  Medical Admin Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='docs'),
    path('api/', include('main.api.v1')),
    path('api/auth/set_password/', accounts_view.set_password_endpoint),
    path('reset_password/<str:creds>', accounts_view.reset_password_view),
    path('verify_phone/<str:creds>', accounts_view.verify_phone_view),
    path('verify_email/<str:creds>', accounts_view.verify_email_view)
]

if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve,
             {'document_root': settings.MEDIA_ROOT}),
        path('static/<path:path>', serve,
             {'document_root': settings.STATIC_ROOT}),
    ]
