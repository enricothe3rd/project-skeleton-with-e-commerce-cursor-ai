import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from skeleton.models import Customer,Order, OrderLine, Product
from skeleton.utils.general.general import Queries, FetchValues
from skeleton.utils.queries.validations.core import validate_number

@csrf_exempt
def create_order(request):
    """
    Creates a new order and adjusts product quantities.
    Returns the order details, including the order ID, in the specified format.
    """
    if request.method == "POST":
        try:
            # Parse the request body using Python's json module
            body = json.loads(request.body)

            # Extract fields
            customer_id = body.get("customer")
            order_lines = body.get("order_lines", [])

            # Validate required fields
            if not all([customer_id, order_lines]):
                return JsonResponse({"status": False, "message": "Missing required fields."}, status=400)

            # Validate numeric fields
            try:
                customer_id = validate_number(customer_id, "int", "customer_id")
            except ValueError as err:
                return JsonResponse({"status": False, "message": str(err)}, status=400)

            # Validate that the customer exists
            customer = Customer.objects.filter(id=customer_id).first()
            if not customer:
                return JsonResponse({"status": False, "message": f"Customer with ID {customer_id} not found."}, status=404)

            # Validate order lines and compute subtotals
            total_subtotal = 0
            processed_order_lines = []
            for line in order_lines:
                try:
                    product_id = validate_number(line.get("product"), "int", "product_id")
                    quantity = validate_number(line.get("quantity"), "int", "quantity")

                    # Fetch the product
                    product = Product.objects.filter(id=product_id).first()
                    if not product:
                        return JsonResponse({"status": False, "message": f"Product with ID {product_id} not found."}, status=404)

                    # Calculate subtotal
                    subtotal = product.price * quantity
                    total_subtotal += subtotal

                    # Check stock availability
                    if product.quantity < quantity:
                        return JsonResponse({"status": False, "message": f"Insufficient stock for product {product.name}."}, status=400)

                    # Deduct the quantity from the product
                    product.quantity -= quantity
                    product.save()

                    # Append processed order line
                    processed_order_lines.append({
                        "product_id": product_id,
                        "quantity": quantity,
                        "subtotal": subtotal,
                    })

                except ValueError as err:
                    return JsonResponse({"status": False, "message": str(err)}, status=400)

            # Use Queries to create the order
            response, order_obj = Queries(Order).execute_create({
                "customer_id": customer_id,
                "order_total": total_subtotal,
            })

            if not response["status"]:
                return JsonResponse(response, status=400)

            # Create order lines
            for line in processed_order_lines:
                line_response, _ = Queries(OrderLine).execute_create({
                    "order_id": order_obj.id,
                    "product_id": line["product_id"],
                    "quantity": line["quantity"],
                    "subtotal": line["subtotal"],
                })

                if not line_response["status"]:
                    return JsonResponse(line_response, status=400)

            # Build the response in the desired format
            response_data = {
                "order_id": order_obj.id,  # Include the order ID in the response
                "customer_id": customer_id,
                "order_total": total_subtotal,
                "order_lines": processed_order_lines,
            }

            return JsonResponse({
                "status": True,
                "message": "Order created successfully.",
                "data": response_data,
            })

        except json.JSONDecodeError:  # Correct exception for invalid JSON
            return JsonResponse({"status": False, "message": "Invalid JSON format."}, status=400)
        except KeyError as key_err:
            return JsonResponse({"status": False, "message": f"Missing key: {str(key_err)}"}, status=400)
        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)}, status=500)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)

@csrf_exempt
def fetch_order(request, order_id):
    """
    Fetches a single order by ID, including product names and prices.
    """
    if request.method == "GET":
        try:
            # Use FetchValues to retrieve the order
            fetcher = FetchValues(Order)
            filters = {"id": order_id}
            order_data = fetcher.fetch_one_row(filters)

            if not order_data:
                return JsonResponse({"status": False, "message": "Order not found."}, status=404)

            # Include order lines in the response
            order_lines = OrderLine.objects.filter(order_id=order_id).values()
            processed_order_lines = []

            for line in order_lines:
                # Fetch the product details
                product = Product.objects.filter(id=line["product_id"]).values("name", "price").first()
                if product:
                    processed_order_lines.append({
                        "product_id": line["product_id"],
                        "product_name": product["name"],
                        "product_price": product["price"],
                        "quantity": line["quantity"],
                        "subtotal": line["subtotal"],
                    })

            # Add processed order lines to the order data
            order_data[0]["order_lines"] = processed_order_lines

            return JsonResponse({"status": True, "data": order_data[0]})

        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)}, status=500)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)

@csrf_exempt
def fetch_orders(request):
    """
    Fetches multiple orders based on optional filters, including product names and prices.
    """
    if request.method == "GET":
        try:
            # Extract query parameters
            customer_id = request.GET.get("customer_id")
            min_order_total = request.GET.get("min_order_total")
            max_order_total = request.GET.get("max_order_total")

            # Build filters dynamically
            filters = {}
            if customer_id:
                filters["customer_id"] = validate_number(customer_id, "int", "customer_id")
            if min_order_total:
                filters["order_total__gte"] = validate_number(min_order_total, "float", "min_order_total")
            if max_order_total:
                filters["order_total__lte"] = validate_number(max_order_total, "float", "max_order_total")

            # Use FetchValues to retrieve orders
            fetcher = FetchValues(Order)
            orders_data = fetcher.fetch_one_row(filters)

            # Include order lines for each order
            for order in orders_data:
                order_lines = OrderLine.objects.filter(order_id=order["id"]).values()
                processed_order_lines = []

                for line in order_lines:
                    # Fetch the product details
                    product = Product.objects.filter(id=line["product_id"]).values("name", "price").first()
                    if product:
                        processed_order_lines.append({
                            "product_id": line["product_id"],
                            "product_name": product["name"],
                            "product_price": product["price"],
                            "quantity": line["quantity"],
                            "subtotal": line["subtotal"],
                        })

                # Add processed order lines to the order
                order["order_lines"] = processed_order_lines

            return JsonResponse({"status": True, "data": orders_data})

        except ValueError as val_err:
            return JsonResponse({"status": False, "message": str(val_err)}, status=400)
        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)}, status=500)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)

@csrf_exempt
def update_order(request, order_id):
    """
    Updates an existing order and adjusts product quantities.
    Automatically recalculates subtotals and order total.
    """
    if request.method == "PUT":
        try:
            # Parse the request body
            body = json.loads(request.body)

            # Extract fields
            order_lines = body.get("order_lines", [])

            # Validate required fields
            if not order_lines:
                return JsonResponse({"status": False, "message": "Missing required fields."}, status=400)

            # Fetch the existing order
            order = Order.objects.filter(id=order_id).first()
            if not order:
                return JsonResponse({"status": False, "message": "Order not found."}, status=404)

            # Process updated order lines
            existing_lines = OrderLine.objects.filter(order_id=order_id)
            existing_line_data = {line.product_id: line.quantity for line in existing_lines}

            total_subtotal = 0
            processed_order_lines = []

            for updated_line in order_lines:
                try:
                    product_id = validate_number(updated_line.get("product"), "int", "product_id")
                    quantity = validate_number(updated_line.get("quantity"), "int", "quantity")

                    # Fetch the product
                    product = Product.objects.filter(id=product_id).first()
                    if not product:
                        return JsonResponse({"status": False, "message": f"Product with ID {product_id} not found."}, status=404)

                    # Calculate subtotal
                    subtotal = product.price * quantity
                    total_subtotal += subtotal

                    # Calculate the difference in quantity
                    previous_quantity = existing_line_data.get(product_id, 0)
                    quantity_difference = quantity - previous_quantity

                    # Adjust the product quantity
                    if quantity_difference > 0:
                        if product.quantity < quantity_difference:
                            return JsonResponse({"status": False, "message": f"Insufficient stock for product {product.name}."}, status=400)
                        product.quantity -= quantity_difference
                    elif quantity_difference < 0:
                        product.quantity += abs(quantity_difference)

                    product.save()

                    # Update or create the order line
                    if previous_quantity > 0:
                        # Update existing order line
                        line_response, _ = Queries(OrderLine).execute_change({
                            "quantity": quantity,
                            "subtotal": subtotal,
                        }, product_id)
                    else:
                        # Create new order line
                        line_response, _ = Queries(OrderLine).execute_create({
                            "order_id": order_id,
                            "product_id": product_id,
                            "quantity": quantity,
                            "subtotal": subtotal,
                        })

                    if not line_response["status"]:
                        return JsonResponse(line_response, status=400)

                    # Append processed order line
                    processed_order_lines.append({
                        "product_id": product_id,
                        "quantity": quantity,
                        "subtotal": subtotal,
                    })

                except ValueError as err:
                    return JsonResponse({"status": False, "message": str(err)}, status=400)

            # Update the order total
            response, _ = Queries(Order).execute_change({"order_total": total_subtotal}, order_id)
            if not response["status"]:
                return JsonResponse(response, status=400)

            # Build the response in the desired format
            response_data = {
                "order_id": order_id,
                "customer_id": order.customer_id,
                "order_total": total_subtotal,
                "order_lines": processed_order_lines,
            }

            return JsonResponse({
                "status": True,
                "message": "Order updated successfully.",
                "data": response_data,
            })

        except KeyError as key_err:
            return JsonResponse({"status": False, "message": f"Missing key: {str(key_err)}"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"status": False, "message": "Invalid JSON format."}, status=400)
        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)}, status=500)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)

@csrf_exempt
def delete_order(request, order_id):
    """
    Deletes an order and restores product quantities.
    """
    if request.method == "DELETE":
        try:
            # Fetch the existing order
            order = Order.objects.filter(id=order_id).first()
            if not order:
                return JsonResponse({"status": False, "message": "Order not found."}, status=404)

            # Fetch existing order lines
            existing_lines = OrderLine.objects.filter(order_id=order_id)

            # Restore product quantities
            for line in existing_lines:
                product = line.product
                product.quantity += line.quantity
                product.save()

            # Delete the order
            response, _ = Queries(Order).execute_unrestricted_delete(order_id)
            if not response["status"]:
                return JsonResponse(response, status=400)

            return JsonResponse({"status": True, "message": "Order deleted successfully."})

        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)}, status=500)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)