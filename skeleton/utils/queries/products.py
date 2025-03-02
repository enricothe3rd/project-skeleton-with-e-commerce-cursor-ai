from skeleton.models import Product
import json
from skeleton.utils.general.general import Queries, EvaluateQueryResults, ParseValues, FetchValues
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from skeleton.utils.queries.validations.core import validate_number

@csrf_exempt
def create_product(request):
    """
    Creates a new product using the Queries utility.
    """
    if request.method == "POST":
        try:
            # Parse the request body
            body = json.loads(request.body)

            # Extract fields
            name = body.get("name")
            quantity = body.get("quantity")
            price = body.get("price")
            expiration_date = body.get("expiration_date")

            # Validate required fields
            if name is None or quantity is None or price is None:
                return JsonResponse({"status": False, "message": "Missing required fields."}, status=400)

            # Validate quantity and price using the reusable function
            try:
                quantity = validate_number(quantity, "int", "quantity")
                price = validate_number(price, "float", "price")
            except ValueError as err:
                return JsonResponse({"status": False, "message": str(err)}, status=400)

            # Parse expiration_date from string to datetime
            try:
                parsed_expiration_date = ParseValues([expiration_date]).parse_date_from_string()[0]
            except ValueError as date_err:
                return JsonResponse({"status": False, "message": f"Invalid date format: {str(date_err)}"}, status=400)

            # Prepare parameters for creation
            params = {
                "name": name,
                "quantity": quantity,
                "price": price,
                "expiration_date": parsed_expiration_date,
            }

            # Use Queries to create the product
            response, _ = Queries(Product).execute_create(params)

            # Return the response
            return JsonResponse(response)

        except KeyError as key_err:
            return JsonResponse({"status": False, "message": f"Missing key: {str(key_err)}"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"status": False, "message": "Invalid JSON format."}, status=400)
        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)}, status=500)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)

@csrf_exempt
def update_product(request, product_id):
    """
    Updates an existing product using the Queries utility.
    """
    if request.method == "PUT":
        try:
            # Parse the request body
            body = json.loads(request.body)

            # Validate quantity and price if they exist in the request
            if "quantity" in body:
                try:
                    body["quantity"] = validate_number(body["quantity"], "int", "quantity")
                except ValueError as err:
                    return JsonResponse({"status": False, "message": str(err)}, status=400)

            if "price" in body:
                try:
                    body["price"] = validate_number(body["price"], "float", "price")
                except ValueError as err:
                    return JsonResponse({"status": False, "message": str(err)}, status=400)

            # Use Queries to update the product
            response, _ = Queries(Product).execute_change(body, product_id)

            # Return the response
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": False, "message": "Invalid JSON format."}, status=400)
        except KeyError as key_err:
            return JsonResponse({"status": False, "message": f"Missing key: {str(key_err)}"}, status=400)
        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)}, status=500)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)


def fetch_products(request):
    """
    Fetches products based on optional filters or by ID.
    """
    if request.method == "GET":
        try:
            # Extract query parameters
            product_id = request.GET.get("id")
            name = request.GET.get("name")

            # Build filters dynamically
            filters = {}
            if name:
                filters["name__icontains"] = name

            # Fetch a single product by ID
            if product_id:
                try:
                    product = Product.objects.filter(id=product_id).values().first()
                    if not product:
                        return JsonResponse({"status": False, "message": "Product not found."})
                    return JsonResponse({"status": True, "data": product})
                except Exception as ex:
                    return JsonResponse({"status": False, "message": str(ex)})

            # Fetch multiple products with optional filters
            products = Product.objects.filter(**filters).values()
            return JsonResponse({"status": True, "data": list(products)})

        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)})
    return JsonResponse({"status": False, "message": "Invalid request method."})

def delete_product(request, product_id):
    """
    Deletes a product using the Queries utility.
    """
    if request.method == "DELETE":
        try:
            # Use Queries to delete the product
            response, _ = Queries(Product).execute_restricted_delete(product_id)

            # Return the response
            return JsonResponse(response)

        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)})
    return JsonResponse({"status": False, "message": "Invalid request method."})