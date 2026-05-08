from django.urls import path
from . import views

# Use <str:> instead of <slug:> so Cyrillic slugs are matched correctly.
# Django's built-in <slug:> converter only accepts ASCII [a-zA-Z0-9_-].
urlpatterns = [
    path('', views.CatalogView.as_view(), name='catalog'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('<str:category_slug>/', views.CategoryView.as_view(), name='category'),
    path('<str:category_slug>/<str:product_slug>/', views.ProductDetailView.as_view(), name='product-detail'),
]
