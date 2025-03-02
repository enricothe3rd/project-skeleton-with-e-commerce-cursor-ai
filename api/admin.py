from django.contrib import admin
from .models import Product, Customer, Order, OrderLine

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'price', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'tin_number', 'created_at', 'updated_at')
    search_fields = ('name', 'tin_number')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('transaction_code', 'customer', 'order_total', 'created_at', 'updated_at')
    search_fields = ('transaction_code', 'customer__name')

@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'subtotal', 'created_at', 'updated_at')
    search_fields = ('order__transaction_code', 'product__name')