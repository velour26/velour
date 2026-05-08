from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.PageView.as_view(), kwargs={'slug': 'about'}, name='about'),
    path('delivery/', views.PageView.as_view(), kwargs={'slug': 'delivery'}, name='delivery'),
    path('contacts/', views.PageView.as_view(), kwargs={'slug': 'contacts'}, name='contacts'),
    path('returns/', views.PageView.as_view(), kwargs={'slug': 'returns'}, name='returns'),
    path('privacy/', views.PageView.as_view(), kwargs={'slug': 'privacy'}, name='privacy'),
    path('terms/', views.PageView.as_view(), kwargs={'slug': 'terms'}, name='terms'),
]
