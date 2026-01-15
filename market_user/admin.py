from django.contrib import admin
from market_user.models import Cart, CartItem, Order, OrderItem





@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    search_fields = ('product__title', 'cart__user__username')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'total_price')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('product__title', 'order__user__username')



'''
fields = Admin panelda formaning qaysi fieldlar ko‘rsatilishi va qanday guruhlanishini belgilaydi.
list_editable = Ro‘yxatda to‘g‘ridan-to‘g‘ri o‘zgartirish mumkin bo‘lgan ustunlarni belgilaydi.
search_fields = Admin panelda qaysi fieldlar bo‘yicha qidirish mumkinligini belgilaydi.
list_filter = Chap panelda filter qilish imkoniyati qo‘yadi, masalan status yoki turi bo‘yicha saralash.
readonly_fields = Bu fieldlar admin panelida tahrirlanmasin deyish uchun.
ordering = Ro‘yxatni qaysi tartibda ko‘rsatish kerakligini belgilaydi.
'''
