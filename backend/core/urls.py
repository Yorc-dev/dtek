from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView

from . import settings

docs_urls = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

# from axes.decorators import axes_dispatch

# убираем декоратор Axes только для админки
# admin.site.login = axes_dispatch(admin.site.login)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', include(docs_urls)),
    path('api/v1/account/', include('apps.account.urls')),
    path('api/v1/application/', include('apps.application.urls')),
    path('api/v1/license/', include('apps.license_template.urls')),
    path('api/v1/documents/', include('apps.document.urls')),
    path('api/v1/decree/', include('apps.decree.urls')),
    path('api/v1/organization/', include('apps.organization.urls')),
    path("", include('django_prometheus.urls')),
    path('tinymce/', include('tinymce.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


