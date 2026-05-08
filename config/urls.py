from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('api/', include('apps.api.urls')),

    # Frontend pages
    path('', include('apps.pages.urls')),
    path('catalog/', include('apps.catalog.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('account/', include('apps.accounts.urls')),
    path('newsletter/', include('apps.newsletter.urls')),
]

# Медиафайлы отдаём всегда — они лежат в репозитории и деплоятся вместе с кодом
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
