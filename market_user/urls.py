from django.urls import path
from .views import CartAPIView, CartItemPutAPIView, CartItemPatchAPIView, CartItemDeleteAPIView, OrderCreateAPIView, OrderListAPIView

urlpatterns = [
    path('cart/', CartAPIView.as_view(), name='cart-detail'),
    path('cart/item/put/', CartItemPutAPIView.as_view(), name='cart-item-put'),
    path('cart/item/patch/', CartItemPatchAPIView.as_view(), name='cart-item-patch'),
    path('cart/item/delete/', CartItemDeleteAPIView.as_view(), name='cart-item-delete'),

    path('order/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/', OrderListAPIView.as_view(), name='orders-list'),
]
