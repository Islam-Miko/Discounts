from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .swagger import urlpatterns as swagger_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/v1/",
        include("discounts.urls"),
    ),
    path(
        "__debug__/",
        include("debug_toolbar.urls"),
    ),
    path("api/v1/", include("authentication.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += swagger_urlpatterns
