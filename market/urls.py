from django.urls import path
from .views import ProductCommentsAPIView, CommentCreateAPIView, CommentUpdateAPIView, CommentDeleteAPIView, \
    CategoryAPIView, ProductAPIView, ProductDetailAPIView

urlpatterns = [
    path('categories/', CategoryAPIView.as_view()),
    path('products/', ProductAPIView.as_view()),
    path('products/<int:pk>/product/detail/', ProductDetailAPIView.as_view()),

    path('products/comments/', ProductCommentsAPIView.as_view()),
    path('products/<int:product_id>/comments/add/', CommentCreateAPIView.as_view()),
    path('comments/<int:comment_id>/update/', CommentUpdateAPIView.as_view()),
    path('comments/<int:comment_id>/delete/', CommentDeleteAPIView.as_view())
]



