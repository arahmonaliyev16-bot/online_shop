from django.contrib import admin
from market.models import Category, Products, Comment




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'stock', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('category', 'is_active')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'created_at')
    search_fields = ('product__title', 'user__username', 'text')  # product va user orqali qidirish
    list_filter = ('rating',)
    readonly_fields = ('created_at', 'updated_at')