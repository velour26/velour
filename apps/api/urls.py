from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.api.views.catalog import CategoryViewSet, ProductViewSet, FilterGroupListView, BrandListView
from apps.api.views.cart import CartView, CartItemAddView, CartItemUpdateView
from apps.api.views.orders import CreateOrderView, OrderListView, OrderDetailView, OrderCancelView
from apps.api.views.accounts import (
    LoginView, LogoutView, RegisterView, ProfileView, ChangePasswordView,
    AddressListCreateView, AddressDetailView
)
from apps.api.views.newsletter import SubscribeView, ConfirmSubscriptionView, UnsubscribeView
from apps.api.views.favorites import FavoriteListView, FavoriteToggleView, FavoriteStatusView

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),

    # Filters & Brands
    path('filters/', FilterGroupListView.as_view(), name='api-filters'),
    path('brands/', BrandListView.as_view(), name='api-brands'),

    # Cart
    path('cart/', CartView.as_view(), name='api-cart'),
    path('cart/add/', CartItemAddView.as_view(), name='api-cart-add'),
    path('cart/items/<int:item_id>/', CartItemUpdateView.as_view(), name='api-cart-item'),

    # Orders
    path('orders/', OrderListView.as_view(), name='api-orders'),
    path('orders/create/', CreateOrderView.as_view(), name='api-order-create'),
    path('orders/<str:number>/', OrderDetailView.as_view(), name='api-order-detail'),
    path('orders/<str:number>/cancel/', OrderCancelView.as_view(), name='api-order-cancel'),

    # Accounts
    path('auth/login/', LoginView.as_view(), name='api-login'),
    path('auth/logout/', LogoutView.as_view(), name='api-logout'),
    path('auth/register/', RegisterView.as_view(), name='api-register'),
    path('auth/profile/', ProfileView.as_view(), name='api-profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='api-change-password'),
    path('auth/addresses/', AddressListCreateView.as_view(), name='api-addresses'),
    path('auth/addresses/<int:pk>/', AddressDetailView.as_view(), name='api-address-detail'),

    # Favorites
    path('favorites/', FavoriteListView.as_view(), name='api-favorites'),
    path('favorites/status/', FavoriteStatusView.as_view(), name='api-favorites-status'),
    path('favorites/<int:product_id>/', FavoriteToggleView.as_view(), name='api-favorite-toggle'),

    # Newsletter
    path('newsletter/subscribe/', SubscribeView.as_view(), name='api-subscribe'),
    path('newsletter/confirm/<str:token>/', ConfirmSubscriptionView.as_view(), name='api-confirm-sub'),
    path('newsletter/unsubscribe/', UnsubscribeView.as_view(), name='api-unsubscribe'),
]
