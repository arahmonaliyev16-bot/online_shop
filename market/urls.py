from django.urls import path
from .views import ProductListCreateAPIView, ProductDetailAPIView, ProductCommentsAPIView, CommentCreateAPIView, CommentUpdateAPIView, CommentDeleteAPIView

urlpatterns = [
    path('products/', ProductListCreateAPIView.as_view()),
    path('products/<int:pk>/', ProductDetailAPIView.as_view()),

    path('products/<int:product_id>/comments/', ProductCommentsAPIView.as_view()),
    path('products/<int:product_id>/comments/add/', CommentCreateAPIView.as_view()),

    path('comments/<int:comment_id>/update/', CommentUpdateAPIView.as_view()),
    path('comments/<int:comment_id>/delete/', CommentDeleteAPIView.as_view()),
]
