from django.contrib import admin
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('books.urls')),
    path('accounts/', include('accounts.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]