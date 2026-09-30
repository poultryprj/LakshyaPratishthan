# LakshyaPratishthan/urls.py (FINAL CORRECT VERSION)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

urlpatterns = [
    # UNIQUE PATH for the admin site
    path('LakshyaPratishthan/admin/', admin.site.urls),

    # UNIQUE PATH for the mobile_api app
    path('LakshyaPratishthan/mobile/', include('mobile_api.urls')),

    # UNIQUE PATH for the api app
    path('LakshyaPratishthan/api/', include('api.urls')),

    path('LakshyaPratishthan/electionapi/', include('electionapi.urls')),

    path('LakshyaPratishthan/lakshadmin/', include('admin_pannel.urls')),


    re_path(r'^LakshyaPratishthan/media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)