from skeleton.models import Customer, Order
import json
from skeleton.utils.general.general import Queries, EvaluateQueryResults
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from skeleton.utils.queries.validations.core import validate_string  # Import the reusable validation


@csrf_exempt
@csrf_exempt
def create_customer(request):
    """
    Creates a new customer using the Queries utility.
    """
    if request.method == "POST":
        try:
            # Parse the request body
            body = json.loads(request.body)

            # Extract fields
            name = body.get("name")
            address = body.get("address")
            tin_number = body.get("tin_number")

            # Validate required fields
            if not all([name, address, tin_number]):
                return JsonResponse({"status": False, "message": "Missing required fields."}, status=400)

            # Validate that fields are strings
            try:
                name = validate_string(name, "name")
                address = validate_string(address, "address")
                tin_number = validate_string(tin_number, "tin_number")
            except ValueError as err:
                return JsonResponse({"status": False, "message": str(err)}, status=400)

            # Prepare parameters for creation
            params = {
                "name": name,
                "address": address,
                "tin_number": tin_number,
            }

            # Use Queries to create the customer
            response, _ = Queries(Customer).execute_create(params)

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
def update_customer(request, customer_id):
    """
    Updates an existing customer using the Queries utility.
    Ensures the customer exists before performing the update.
    """
    if request.method == "PUT":
        try:
            # Parse the request body
            body = json.loads(request.body)

            # Extract fields
            name = body.get("name")
            address = body.get("address")
            tin_number = body.get("tin_number")

            # Validate that the customer exists
            customer = Customer.objects.filter(id=customer_id).first()
            if not customer:
                return JsonResponse({"status": False, "message": f"Customer with ID {customer_id} not found."}, status=404)

            # Build the update parameters dynamically
            params = {}
            if name:
                try:
                    params["name"] = validate_string(name, "name")
                except ValueError as err:
                    return JsonResponse({"status": False, "message": str(err)}, status=400)

            if address:
                try:
                    params["address"] = validate_string(address, "address")
                except ValueError as err:
                    return JsonResponse({"status": False, "message": str(err)}, status=400)

            if tin_number:
                try:
                    params["tin_number"] = validate_string(tin_number, "tin_number")
                except ValueError as err:
                    return JsonResponse({"status": False, "message": str(err)}, status=400)

            # Use Queries to update the customer
            response, _ = Queries(Customer).execute_change(params, customer_id)

            # Return the response
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": False, "message": "Invalid JSON format."}, status=400)
        except KeyError as key_err:
            return JsonResponse({"status": False, "message": f"Missing key: {str(key_err)}"}, status=400)
        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)}, status=500)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)

@csrf_exempt
def batch_create_update_customers(request):
    """
    Handles batch creation or update of multiple customer records.
    """
    if request.method == "POST":
        try:
            # Parse the request body
            body = json.loads(request.body)

            # Ensure the input is a list
            if not isinstance(body, list):
                return JsonResponse({"status": False, "message": "Invalid input format. Expected a list."}, status=400)

            results = []
            for values in body:
                # Determine whether to create or update
                if values.get("id") and values["id"] not in [None, "", 0]:
                    # Update existing customer
                    row_id = values["id"]
                    params = {
                        "name": values.get("name"),
                        "address": values.get("address"),
                        "tin_number": values.get("tin_number"),
                    }
                    results.append(Queries(Customer).execute_change(params, row_id))
                else:
                    # Create new customer
                    params = {
                        "name": values.get("name"),
                        "address": values.get("address"),
                        "tin_number": values.get("tin_number"),
                    }
                    results.append(Queries(Customer).execute_create(params))

            # Evaluate the results of all operations
            if EvaluateQueryResults(results).execute_query_results():
                return JsonResponse({
                    "status": True,
                    "message": "All records were saved/updated successfully!",
                    "error": None,
                })
            else:
                return JsonResponse({
                    "status": False,
                    "message": "Not all records were saved/updated.",
                    "error": None,
                })

        except KeyError as key_err:
            return JsonResponse({"status": False, "message": f"Missing key: {str(key_err)}"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"status": False, "message": "Invalid JSON format."}, status=400)
        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)}, status=500)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)


def fetch_customers(request):
    """
    Fetches customers based on optional filters or by ID.
    """
    if request.method == "GET":
        try:
            # Extract query parameters
            customer_id = request.GET.get("id")
            name = request.GET.get("name")

            # Build filters dynamically
            filters = {}
            if name:
                filters["name__icontains"] = name

            # Fetch a single customer by ID
            if customer_id:
                try:
                    customer = Customer.objects.filter(id=customer_id).values().first()
                    if not customer:
                        return JsonResponse({"status": False, "message": "Customer not found."})
                    return JsonResponse({"status": True, "data": customer})
                except Exception as ex:
                    return JsonResponse({"status": False, "message": str(ex)})

            # Fetch multiple customers with optional filters
            customers = Customer.objects.filter(**filters).values()
            return JsonResponse({"status": True, "data": list(customers)})

        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)})
    return JsonResponse({"status": False, "message": "Invalid request method."})


@csrf_exempt
def delete_customer(request, customer_id):
    """
    Deletes a customer using the Queries utility.
    Prevents deletion if the customer has existing orders.
    """
    if request.method == "DELETE":
        try:
            # Check if the customer exists
            customer = Customer.objects.filter(id=customer_id).first()
            if not customer:
                return JsonResponse({"status": False, "message": f"Customer with ID {customer_id} not found."}, status=404)

            # Check if the customer has existing orders
            has_orders = Order.objects.filter(customer_id=customer_id).exists()
            if has_orders:
                return JsonResponse({"status": False, "message": "Cannot delete customer with existing orders."}, status=400)

            # Use Queries to delete the customer
            response, _ = Queries(Customer).execute_restricted_delete(customer_id)

            # Return the response
            return JsonResponse(response)

        except Exception as ex:
            return JsonResponse({"status": False, "message": str(ex)}, status=500)

    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)