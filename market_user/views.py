from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Order, OrderItem
from market.models import Products
from .serializer import CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartSerializer, CreateOrderSerializer, OrderSerializer, OrderStatusSerializer


# ====================
# CART
# ====================

class CartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema()
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        data = []
        for item in cart.cart_items.all():
            data.append({
                "id": item.id,
                "product_id": item.product.id,
                "product_title": item.product.title,
                "quantity": item.quantity,
                "price": item.product.price
            })

        return Response(data)

# ===========================================

class CartItemPutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["product_id", "quantity"],
            properties={
                "product_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "quantity": openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        )
    )
    def put(self, request):
        product_id = request.data["product_id"]
        quantity = int(request.data["quantity"])

        if quantity <= 0:
            return Response({"message": "Quantity 0 dan katta bo‘lishi kerak"})

        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Products, id=product_id, is_active=True)

        if quantity > product.stock:
            return Response({"message": "Omborda yetarli mahsulot yo‘q"})

        cart_item, _ = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Mahsulot savatchaga qo‘shildi"})

# ============================================

class CartItemPatchAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["product_id", "quantity"],
            properties={
                "product_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "quantity": openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        )
    )
    def patch(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(
            CartItem,
            cart=cart,
            product_id=request.data["product_id"]
        )

        quantity = int(request.data["quantity"])

        if quantity <= 0:
            return Response({"message": "Quantity 0 dan katta bo‘lishi kerak"})

        if quantity > cart_item.product.stock:
            return Response({"message": "Omborda yetarli mahsulot yo‘q"})

        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Quantity yangilandi"})

# ========================================

class CartItemDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["product_id"],
            properties={
                "product_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        )
    )
    def delete(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(
            CartItem,
            cart=cart,
            product_id=request.data["product_id"]
        )

        cart_item.delete()
        return Response({"message": "Mahsulot o‘chirildi"})


# ====================
# ORDER
# ====================

class OrderCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["address", "phone"],
            properties={
                "address": openapi.Schema(type=openapi.TYPE_STRING),
                "phone": openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)

        if not cart.cart_items.exists():
            return Response({"message": "Savatcha bo‘sh"})

        order = Order.objects.create(
            user=request.user,
            address=request.data["address"],
            phone=request.data["phone"],
            total_price=cart.total_price
        )

        for item in cart.cart_items.all():
            if item.quantity > item.product.stock:
                return Response({"message": "Omborda mahsulot yetarli emas"})

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            item.product.stock -= item.quantity
            item.product.save()

        cart.cart_items.all().delete()

        return Response({"message": "Order yaratildi", "order_id": order.id})

# =====================================

class OrderListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema()
    def get(self, request):
        if request.user.is_staff:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)

        data = []
        for order in orders:
            data.append({
                "order_id": order.id,
                "status": order.status,
                "total_price": order.total_price,
                "created_at": order.created_at
            })

        return Response(data)







