import uuid
from contextlib import AbstractContextManager
from datetime import timezone
from shared.models import BaseModel
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group
from users.models import User



class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('market.Products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} --- {self.product.title}"


class Order(models.Model):

    PENDING = 'pending'
    PAID = 'paid'
    SHIPPED = 'shipped'
    COMPLETED = 'completed'

    STATUS_CHOICES = (
        (PENDING, PENDING),
        (PAID, PAID),
        (SHIPPED, SHIPPED),
        (COMPLETED, COMPLETED)
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return self.user.username


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('market.Products', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # order pay qilinadigan narx

    def __str__(self):
        return f"{self.quantity} --- {self.product.title if self.product else 'deleted product'}"
