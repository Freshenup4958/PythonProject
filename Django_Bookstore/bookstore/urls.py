
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path('admin/', admin.site.urls),

    # REST API
    path('api/', include('books.api.urls')),
# API documentation
path(
    'api/schema/',
    SpectacularAPIView.as_view(),
    name='schema',
),
path(
    'api/docs/',
    SpectacularSwaggerView.as_view(url_name='schema'),
    name='swagger-ui',
),

    # JWT authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Existing website
    path('', include('books.urls')),
    path('accounts/', include('accounts.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
