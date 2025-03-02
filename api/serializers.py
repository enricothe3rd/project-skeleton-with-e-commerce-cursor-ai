import uuid
from rest_framework import serializers
from .models import Product, Customer, Order, OrderLine
from django.utils.timezone import localtime
from django.db import transaction
from django.utils.timezone import now
from decimal import Decimal, InvalidOperation

# Convert the time
class TimestampedModelSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return localtime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    def get_updated_at(self, obj):
        return localtime(obj.updated_at).strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        abstract = True  # Ensures this is only used as a base class


class ProductSerializer(TimestampedModelSerializer):
    class Meta(TimestampedModelSerializer.Meta):
        model = Product
        fields = ['id', 'name', 'quantity', 'price', 'expiration_date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def validate_expiration_date(self, value):
        """
        Optional validation for expiration_date.
        Ensure the expiration date is not in the past.
        """
        if value and value < now().date():
            raise serializers.ValidationError("Expiration date cannot be in the past.")
        return value

    def validate_price(self, value):
        """
        Validate that the price can be converted to a Decimal.
        """
        try:
            # Attempt to convert the value to a Decimal
            decimal_value = Decimal(value)

            # Optionally, you can add additional checks here, such as ensuring the price is positive
            if decimal_value < 0:
                raise serializers.ValidationError("Price cannot be negative.")

            return decimal_value
        except (InvalidOperation, TypeError):
            # If conversion fails, raise a ValidationError
            raise serializers.ValidationError("Price must be a valid decimal number.")

class CustomerSerializer(TimestampedModelSerializer):
    class Meta(TimestampedModelSerializer.Meta):
        model = Customer
        fields = ['id', 'name', 'address', 'tin_number', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']



class OrderLineSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField(source='product.price')  # Fetch product price
    subtotal = serializers.SerializerMethodField()  # Calculate subtotal dynamically
    product_name = serializers.ReadOnlyField(source='product.name')  # Fetch product name

    class Meta:
        model = OrderLine
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'subtotal']

    def get_subtotal(self, obj):
        return obj.quantity * obj.product.price  # Calculate subtotal dynamically

class OrderSerializer(serializers.ModelSerializer):
    transaction_code = serializers.ReadOnlyField()  # Auto-generated transaction code
    order_lines = OrderLineSerializer(many=True)  # Nested OrderLine serializer
    customer_name = serializers.SerializerMethodField()  # Add the customer's name

    class Meta:
        model = Order
        fields = [
            'id',
            'transaction_code',
            'customer',  # Keep the customer ID
            'customer_name',  # Include the customer's name
            'order_total',
            'order_lines',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_customer_name(self, obj):
        """Retrieve the customer's name from the related Customer object."""
        return obj.customer.name if obj.customer else "Unknown Customer"

    @transaction.atomic
    def create(self, validated_data):
        """
        Create an order and its associated order lines.
        Deduct stock for each product and calculate the total order amount.
        """
        order_lines_data = validated_data.pop('order_lines', [])
        order = Order.objects.create(**validated_data)
        order_total = 0  # Initialize total

        for line_data in order_lines_data:
            product = line_data['product']
            quantity = line_data['quantity']

            # Validate stock availability
            if product.quantity < quantity:
                raise serializers.ValidationError(f"Not enough stock for product: {product.name}")

            # Deduct stock and calculate subtotal
            product.quantity -= quantity
            product.save()
            subtotal = quantity * product.price
            order_total += subtotal

            # Create OrderLine
            OrderLine.objects.create(order=order, product=product, quantity=quantity, subtotal=subtotal)

        # Set the order total and save the order
        order.order_total = order_total
        order.save()
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update an order and its associated order lines.
        Recalculate stock and order total based on changes.
        """
        order_lines_data = validated_data.pop('order_lines', [])

        # Update order fields (except `order_total`, which will be recalculated)
        instance.customer = validated_data.get('customer', instance.customer)
        instance.save()

        # Track existing order lines
        existing_order_lines = {line.product.id: line for line in instance.order_lines.all()}
        new_order_total = 0

        for line_data in order_lines_data:
            product = line_data['product']
            new_quantity = line_data['quantity']

            if product.id in existing_order_lines:
                # Update existing order line
                order_line = existing_order_lines[product.id]
                old_quantity = order_line.quantity

                if new_quantity > old_quantity:
                    # Check stock before increasing quantity
                    if product.quantity < (new_quantity - old_quantity):
                        raise serializers.ValidationError(f"Not enough stock for product: {product.name}")
                    product.quantity -= (new_quantity - old_quantity)
                else:
                    # Restore stock if quantity is reduced
                    product.quantity += (old_quantity - new_quantity)

                # Update order line details
                order_line.quantity = new_quantity
                order_line.subtotal = new_quantity * product.price
                order_line.save()
            else:
                # New order line - ensure stock is available
                if product.quantity < new_quantity:
                    raise serializers.ValidationError(f"Not enough stock for product: {product.name}")
                product.quantity -= new_quantity

                # Create new order line
                order_line = OrderLine.objects.create(
                    order=instance,
                    product=product,
                    quantity=new_quantity,
                    subtotal=new_quantity * product.price
                )

            product.save()
            new_order_total += order_line.subtotal

        # Remove any order lines that were not in the update request
        for product_id, order_line in existing_order_lines.items():
            if product_id not in [line['product'].id for line in order_lines_data]:
                product = order_line.product
                product.quantity += order_line.quantity  # Restore stock
                product.save()
                order_line.delete()  # Remove from order

        # Update order total
        instance.order_total = new_order_total
        instance.save()
        return instance