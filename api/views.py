from rest_framework.response import Response
from rest_framework import status
from .models import Product, Customer, Order, OrderLine
from .serializers import ProductSerializer, CustomerSerializer, OrderSerializer, OrderLineSerializer
from rest_framework import viewsets
from django.utils import timezone

class ProductViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides `create`, `retrieve`, `update`, `partial_update`, `list`, and `destroy` actions.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Customer CRUD operations.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Override the delete method to prevent deletion if the customer has existing orders.
        """
        customer = self.get_object()
        if customer.orders.exists():
            return Response({"error": "Cannot delete customer with existing orders"}, status=status.HTTP_400_BAD_REQUEST)

        customer.delete()
        return Response({"message": "Customer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)




class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        """Create a new order."""
        # Validate the incoming data using the serializer
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract order lines from the validated data
        order_lines_data = serializer.validated_data.get("order_lines", [])
        for line_data in order_lines_data:
            product = line_data["product"]

            # Check if the product has expired
            if product.expiration_date and product.expiration_date < timezone.now().date():
                return Response(
                    {"error": f"The product '{product.name}' has expired."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Ensure quantity is a number
            quantity = line_data.get("quantity")
            if not isinstance(quantity, (int, float)) or quantity <= 0:
                return Response(
                    {"error": "Quantity must be a positive number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # If all products are valid, save the order
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update an existing order."""
        try:
            order = self.get_object()
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """Update only the quantity of specific order lines."""
        order = self.get_object()
        order_lines_data = request.data.get("order_lines", [])

        for line_data in order_lines_data:
            line_id = line_data.get("id")
            new_quantity = line_data.get("quantity")

            # Ensure id is provided and is a valid integer
            if line_id is None:
                return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Attempt to convert the id to an integer
                line_id = int(line_id)
            except ValueError:
                return Response(
                    {"error": f"Invalid ID: '{line_id}'. ID must be a valid integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Ensure quantity is provided and is a number
            if new_quantity is None:
                return Response({"error": "Quantity is required"}, status=status.HTTP_400_BAD_REQUEST)

            if not isinstance(new_quantity, (int, float)) or new_quantity <= 0:
                return Response(
                    {"error": "Quantity must be a positive number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                order_line = order.order_lines.get(id=line_id)
                order_line.quantity = new_quantity
                order_line.save()
            except OrderLine.DoesNotExist:
                return Response({"error": f"Order line {line_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Order quantity updated successfully"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Delete an order and restore product stock."""
        try:
            order = self.get_object()
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        for line in order.order_lines.all():
            product = line.product
            product.quantity += line.quantity
            product.save()
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        orders = self.get_queryset()
        if not orders.exists():
            return Response({"message": "No orders found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)