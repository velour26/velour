from django.urls import path
from . import views

urlpatterns = [
    path('', views.WarehouseListView.as_view(), name='warehouse-list'),
    path('<int:warehouse_pk>/receipts/', views.ReceiptListView.as_view(), name='warehouse-receipts'),
    path('<int:warehouse_pk>/revisions/', views.RevisionListView.as_view(), name='warehouse-revisions'),
]
