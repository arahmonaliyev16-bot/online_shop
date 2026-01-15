import uuid
from contextlib import AbstractContextManager
from datetime import timezone
from shared.models import BaseModel
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group
from users.models import User

from config import settings


# class MarketUser(AbstractUser):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # primary key UUID
#     username = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=20, blank=True, null=True)
#     photo = models.ImageField(upload_to='users_photo/', null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     email = models.EmailField(unique=True)
#
#     groups = models.ManyToManyField(
#         Group,
#         related_name='marketuser_set',
#         blank=True,
#         help_text='The groups this user belongs to.',
#         verbose_name='groups',
#     )
#     user_permissions = models.ManyToManyField(Permission,
#         related_name='marketuser_permissions_set',
#         blank=True,
#         help_text='Specific permissions for this user.',
#         verbose_name='user permissions')
#
#     def __str__(self):
#         return self.username

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
