from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from shared.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from market.models import Products, Comment
from market.serializer import ProductsSerializer, ProductDetailSerializer, CommentSerializer


# =========================
# PRODUCTS
# =========================

class ProductListCreateAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Productlar ro‘yxati",
        responses={200: ProductsSerializer(many=True)}
    )
    def get(self, request):
        products = Products.objects.filter(is_active=True)
        serializer = ProductsSerializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Product qo‘shish (faqat admin)",
        request_body=ProductsSerializer,
        responses={201: ProductsSerializer}
    )
    def post(self, request):
        serializer = ProductsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Product detail",
        responses={200: ProductDetailSerializer}
    )
    def get(self, request, pk):
        product = get_object_or_404(Products, id=pk, is_active=True)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)


# =========================
# COMMENTS
# =========================

class ProductCommentsAPIView(APIView):

    @swagger_auto_schema(
        operation_summary="Product commentlari",
        responses={200: CommentSerializer(many=True)}
    )
    def get(self, request, product_id):
        product = get_object_or_404(Products, id=product_id, is_active=True)
        comments = product.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Comment qo‘shish",
        request_body=CommentSerializer,
        responses={201: CommentSerializer}
    )
    def post(self, request, product_id):
        product = get_object_or_404(Products, id=product_id, is_active=True)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    @swagger_auto_schema(
        operation_summary="Comment yangilash",
        request_body=CommentSerializer,
        responses={200: CommentSerializer}
    )
    def patch(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CommentDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    @swagger_auto_schema(
        operation_summary="Comment o‘chirish",
        responses={200: openapi.Response("Deleted")}
    )
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        comment.delete()
        return Response({"success": True})
















# class ProductListCreateView(APIView):
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     def get(self, request):
#         products = Products.objects.filter(is_active=True)
#         serializer = ProductsSerializer(products, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         if not request.user.is_staff:
#             data = {
#                 'success': False,
#                 'message': 'Foydalanuvchi admin emas',
#             }
#             return Response(data)
#
#         serializer = ProductsSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
#
# class ProductDetailUpdateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_object(self, pk):
#         try:
#             return Products.objects.get(pk=pk)
#         except Products.DoesNotExist:
#             raise ValidationError("Product topilmadi")
#
#     def get(self, request, pk):
#         product = self.get_object(pk)
#         serializer = ProductsSerializer(product)
#         return Response(serializer.data)
#
#     def put(self, request, pk):
#         if not request.user.is_staff:
#             data = {
#                 'success': False,
#                 'message': 'Foydalanuvchi admin emas',
#             }
#
#
#         product = self.get_object(pk)
#         serializer = ProductsSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#
#
# class CommentCreateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request):
#         serializer = CommentSerializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
#
# class CartView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get(self, request):
#         cart = Cart.objects.get_or_create(user=request.user, is_active=True)
#         serializer = CartSerializer(cart)
#         return Response(serializer.data)
#
#
# class CartItemAddView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request):
#         serializer = CartItemSerializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
#
# class OrderCreateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request):
#         user = request.user
#
#         try:
#             cart = Cart.objects.get(user=user, is_active=True)
#         except Cart.DoesNotExist:
#             data = {
#                 'success': False,
#                 'message': 'Cart bosh'
#             }
#             return Response(data)
#
#         # total_price hisoblash
#         total_price = sum([item.product.price * item.quantity for item in cart.cart_items.all()])
#
#         # Order yaratish
#         order = Order.objects.create(user=user, total_price=total_price, status='pending')
#
#         # CartItem → OrderItem
#         for item in cart.cart_items.all():
#             order.items.create(
#                 product=item.product,
#                 quantity=item.quantity,
#                 price=item.product.price
#             )
#
#
#         cart.cart_items.all().delete()
#         cart.is_active = False
#         cart.save()
#
#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
