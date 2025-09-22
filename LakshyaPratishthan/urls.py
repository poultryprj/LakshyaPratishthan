# LakshyaPratishthan/urls.py (FINAL CORRECT VERSION)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # UNIQUE PATH for the admin site
    path('LakshyaPratishthan/admin/', admin.site.urls),

    # UNIQUE PATH for the mobile_api app
    path('LakshyaPratishthan/mobile/', include('mobile_api.urls')),

    # UNIQUE PATH for the api app
    path('LakshyaPratishthan/api/', include('api.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)