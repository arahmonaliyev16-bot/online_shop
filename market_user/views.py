from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Order, OrderItem
from market.models import Products
from .serializer import CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartSerializer, CreateOrderSerializer, OrderSerializer, OrderStatusSerializer


# ------------------- CART -------------------

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Products, id=serializer.validated_data['product_id'])
        quantity = serializer.validated_data['quantity']

        if product.stock < quantity:
            return Response(
                {"error": "Omborda mahsulot yetarli emas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                return Response(
                    {"error": "Omborda mahsulot yetarli emas."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)


class CartItemUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = UpdateCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_object_or_404(Cart, user=request.user)
        product = get_object_or_404(Products, id=serializer.validated_data['product_id'])
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        quantity = serializer.validated_data['quantity']

        if quantity > product.stock:
            return Response({"error": "Omborda mahsulot yetarli emas."}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)


class CartItemRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UpdateCartSerializer(data=request.data)  # yoki alohida RemoveCartSerializer
        serializer.is_valid(raise_exception=True)

        cart = get_object_or_404(Cart, user=request.user)
        product = get_object_or_404(Products, id=serializer.validated_data['product_id'])
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.delete()
        return Response({"message": "Product removed from cart"})


class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart.cart_items.all().delete()
        return Response({"message": "Cart cleared"})


# ------------------- ORDERS -------------------

class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_object_or_404(Cart, user=request.user)
        if not cart.cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Stock tekshirish
        for item in cart.cart_items.all():
            if item.product.stock < item.quantity:
                return Response(
                    {"error": f"{item.product.name} uchun omborda yetarli mahsulot yo'q"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        order = Order.objects.create(
            user=request.user,
            total_price=cart.total_price,
            shipping_address=serializer.validated_data['shipping_address'],
            phone=serializer.validated_data['phone'],
            notes=serializer.validated_data.get('notes', '')
        )

        for item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        cart.cart_items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrdersListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        if request.user.is_staff:
            order = get_object_or_404(Order, id=order_id)
        else:
            order = get_object_or_404(Order, id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order.status = serializer.validated_data['status']
        order.save()
        return Response(OrderSerializer(order).data)


class OrderCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status != 'pending':
            return Response({"error": "Only pending orders can be cancelled"}, status=status.HTTP_400_BAD_REQUEST)

        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()

        order.status = 'canceled'
        order.save()
        return Response({"message": "Order cancelled"})
