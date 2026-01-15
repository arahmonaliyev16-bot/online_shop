from django.urls import path
from .views import (
    CartView, CartItemAddView, CartItemUpdateView, CartItemRemoveView, CartClearView,
    OrderCreateView, OrdersListView, OrderDetailView, OrderStatusUpdateView, OrderCancelView
)

urlpatterns = [
    # ----- CART -----
    path('cart/', CartView.as_view(), name='cart-detail'),
    path('add_cart/', CartItemAddView.as_view(), name='cart-add-item'),
    path('update_cart/', CartItemUpdateView.as_view(), name='cart-update-item'),
    path('remove_cart/', CartItemRemoveView.as_view(), name='cart-remove-item'),
    path('clear_cart/', CartClearView.as_view(), name='cart-clear'),

    # ----- ORDERS -----
    path('create_order/', OrderCreateView.as_view(), name='order-create'),
    path('orders/', OrdersListView.as_view(), name='orders-list'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:order_id>/update_status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('orders/<int:order_id>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
]
