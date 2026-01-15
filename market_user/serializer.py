from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Cart, CartItem, Order, OrderItem
from market.models import Products
# from market.serializer import ProductsSerializer
from users.models import User



# ================= MarketUser =================
class MarketUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'phone_number')


# ================= Cart =================
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('id', 'is_active')

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise ValidationError("Siz login qilmagan ekansiz.")
        validated_data['user'] = user
        return super().create(validated_data)


# ================= CartItem =================
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('product', 'quantity')

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise ValidationError("Siz login qilmagan ekansiz.")

        # Har doim faqat active cart bilan ishlaydi
        cart, created = Cart.objects.get_or_create(user=user, is_active=True)
        validated_data['cart'] = cart
        return super().create(validated_data)


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value = 1, default =1)

    def validate_product_id(self, value):
        try:
            product = Products.objects.get(id=value, is_active=True)
            if product.stock < 1:
                raise serializers.ValidationError("Mahsulot omborda yo'q")
        except Products.DoesNotExist:
            raise serializers.ValidationError("Could not find the product")
        return value

class UpdateCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value = 1)

class RemoveFromCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

# ================= Order =================
class OrderSerializer(serializers.ModelSerializer):
    read_only_fields = ['id', 'user', 'total_price', 'created_at', 'updated_at']
    class Meta:
        model = Order
        fields = ('id', 'user', 'total_price', 'status')


class CreateOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    phone = serializers.CharField(max_length = 20)
    notes = serializers.CharField(required = False, allow_blank = True)


# ================= OrderItem =================
class OrderItemSerializer(serializers.ModelSerializer):
    # product = ProductsSerializer(read_only=True)
    subtotal = serializers.ReadOnlyField()
    class Meta:
        model = OrderItem
        fields = ('order', 'product', 'quantity', 'price')


class OrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)