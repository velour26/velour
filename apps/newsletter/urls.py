from django.urls import path
from . import views

urlpatterns = [
    path('confirm/<str:token>/', views.ConfirmView.as_view(), name='newsletter-confirm'),
    path('unsubscribe/', views.UnsubscribePageView.as_view(), name='newsletter-unsubscribe'),
]
