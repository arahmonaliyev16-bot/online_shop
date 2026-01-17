from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from unicodedata import category

from shared.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from market.models import Products, Comment, Category
from market.serializer import ProductsSerializer, ProductDetailSerializer, CommentSerializer, CategorySerializer



# =========================
# CATEGORY
# =========================

class CategoryAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema()
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        data_list = []

        for category in categories:
            data_list.append({
                "id": category.id,
                "title": category.title,
                "description": category.description,
                "products_count": category.products.filter(is_active=True).count()
            })

        return Response(data_list, status=status.HTTP_200_OK)



# =========================
# PRODUCTS
# =========================

class ProductAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema()
    def get(self, request):
        products = Products.objects.filter(is_active=True)
        data_list = []

        for product in products:
            data_list.append({
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "price": product.price,
                "category": {
                    "id": product.category.id,
                    "title": product.category.title,
                    "description": product.category.description,
                    "products_count": product.category.products.filter(is_active=True).count()
                }
            })

        return Response(data_list, status=status.HTTP_200_OK)
#

class ProductDetailAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema()
    def get(self, request, pk):
        try:
            product = Products.objects.get(id=pk, is_active=True)
        except Products.DoesNotExist:
            return Response({
                "success": False,
                "message": "Bunday mahsulot yo‘q"
            }, status=status.HTTP_404_NOT_FOUND)

        data = {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "price": product.price,
            "category": {
                "id": product.category.id,
                "title": product.category.title,
                "description": product.category.description,
                "products_count": product.category.products.filter(is_active=True).count()
            }
        }

        return Response(data)



# =========================
# COMMENTS
# =========================

class ProductCommentsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_comments = Comment.objects.filter(user=request.user).select_related('product')
        product_dict = {}
        for comment in user_comments:
            product = comment.product
            if product.title not in product_dict:
                product_dict[product.title] = []
            product_dict[product.title].append({
                "id": comment.id,
                "text": comment.text,
                "created_at": comment.created_at,
            })

        data_list = []
        for title, comments in product_dict.items():
            data_list.append({
                "product_title": title,
                "comments": comments
            })

        return Response(data_list)

# ==========================
# CREATE COMMENT
# ==========================

class CommentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],  # rating optional
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, example="Bu mening kommentim"),
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER, example=5)
            }
        )
    )
    def post(self, request, product_id):
        product = get_object_or_404(Products, id=product_id, is_active=True)
        serializer = CommentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product=product)  # user va product to‘g‘ri uzatiladi
        return Response(serializer.data, status=201)


# ==========================
# UPDATE COMMENT
# ==========================
class CommentUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, example="Yangilangan komment"),
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER, example=4)
            }
        )
    )
    def patch(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        serializer = CommentSerializer(comment, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)


# ==========================
# DELETE COMMENT
# ==========================
class CommentDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    @swagger_auto_schema()
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        comment.delete()
        return Response({'success': True}, status=204)
