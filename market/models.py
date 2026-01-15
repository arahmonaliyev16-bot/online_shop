from django.db import models
from users.models import UserConfirmation



class Category(models.Model):
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Products(models.Model):

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=50,)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, null=True)
    stock = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        comments = self.comments.all()
        if comments.exists():
            return sum(c.rating for c in comments) / comments.count()
        return 0


class Comment(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(UserConfirmation, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
