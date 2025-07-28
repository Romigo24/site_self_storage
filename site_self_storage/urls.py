from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from storage.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('storage.urls', 'storage'), namespace='storage')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path("select2/", include("django_select2.urls")),
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
