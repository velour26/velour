from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/<str:order_number>/', views.PaymentView.as_view(), name='payment'),
    path('success/<str:order_number>/', views.OrderSuccessView.as_view(), name='order-success'),
    path('sbp-success/<str:order_number>/', views.SBPSuccessView.as_view(), name='sbp-success'),
    path('my/', views.MyOrdersView.as_view(), name='my-orders'),
    path('my/<str:number>/', views.OrderDetailView.as_view(), name='order-detail'),
]
