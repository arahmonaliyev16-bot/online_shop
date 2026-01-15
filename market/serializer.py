from rest_framework import serializers
from market.models import Category, Products, Comment
from users.serializers import SignUpSerializer


# ================= Category =================
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'description')

    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()


# ================= Products =================
class ProductsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only =True)
    average_rating = serializers.ReadOnlyField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = [
            'id', 'title', 'description', 'price', 'category', 'category_id',
            'image', 'stock', 'is_active', 'average_rating', 'comments_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_comments_count(self, obj):
        return obj.comments.count()


# ================= Comment =================
class CommentSerializer(serializers.ModelSerializer):
    user = SignUpSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductDetailSerializer(ProductsSerializer):
    comments = CommentSerializer(many = True, read_only=True)

    class Meta(ProductsSerializer.Meta):
        fields = ProductsSerializer.Meta.fields + ['comments']
