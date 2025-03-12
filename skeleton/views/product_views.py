import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from skeleton.models import Product
from skeleton.utils.general.BuildHttpResponse import BuildResponse
from skeleton.utils.general.general import Queries, EvaluateQueryResults
from skeleton.utils.queries.validations.core import validate_number, validate_string
from decimal import Decimal
from datetime import datetime, date

@csrf_exempt
def create_product(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            
            # Validate inputs
            name = validate_string(data.get('name'), 'name')
            quantity = validate_number(data.get('quantity'), 'int', 'quantity')
            price = validate_number(data.get('price'), 'float', 'price')
            expiration_date = data.get('expiration_date')  # Can be null
            
            params = {
                'name': name,
                'quantity': quantity,
                'price': price,
                'expiration_date': expiration_date
            }
            
            result = Queries(Product).execute_create(params)
            
            if result[0]['status']:
                return JsonResponse({
                    'status': True,
                    'message': 'Product created successfully',
                    'data': result[0]['values']
                })
            else:
                return JsonResponse({
                    'status': False,
                    'message': result[0]['message']
                }, status=400)
                
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def update_product(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            product_id = data.get('id')
            
            if not product_id:
                return JsonResponse({'error': 'Product ID is required'}, status=400)
            
            # Validate inputs
            params = {}
            if 'name' in data:
                params['name'] = validate_string(data['name'], 'name')
            if 'quantity' in data:
                quantity = validate_number(data['quantity'], 'int', 'quantity')
                if quantity < 0:
                    return JsonResponse({'error': 'Quantity cannot be negative'}, status=400)
                params['quantity'] = quantity
            if 'price' in data:
                params['price'] = validate_number(data['price'], 'float', 'price')
            if 'expiration_date' in data:
                params['expiration_date'] = data['expiration_date']
            
            result = Queries(Product).execute_change(params, product_id)
            
            if result[0]['status']:
                return JsonResponse({
                    'status': True,
                    'message': 'Product updated successfully',
                    'data': result[0]['values']
                })
            else:
                return JsonResponse({
                    'status': False,
                    'message': result[0]['message']
                }, status=400)
                
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def delete_product(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            product_id = data.get('id')
            
            if not product_id:
                return JsonResponse({'error': 'Product ID is required'}, status=400)
            
            result = Queries(Product).execute_unrestricted_delete(product_id)
            
            if result[0]['status']:
                return JsonResponse({
                    'status': True,
                    'message': 'Product deleted successfully'
                })
            else:
                return JsonResponse({
                    'status': False,
                    'message': result[0]['message']
                }, status=400)
                
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def fetch_products(request):
    try:
        if request.method == 'GET':
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            search = request.GET.get('search', '')
            
            # Query products with optional search and ordering
            products = Product.objects.all().order_by('id')  # Ensure consistent ordering
            if search:
                products = products.filter(name__icontains=search)
            
            # Apply pagination
            paginator = Paginator(products, page_size)
            current_page = paginator.get_page(page)
            
            # Preprocess the items to handle Decimal, datetime, and date fields
            items = []
            for product in current_page.object_list.values():
                processed_product = {
                    key: float(value) if isinstance(value, Decimal) else
                         value.isoformat() if isinstance(value, (datetime, date)) else
                         value
                    for key, value in product.items()
                }
                items.append(processed_product)
            
            # Prepare response body
            response_body = {
                'status': True,
                'message': 'Products fetched successfully',
                'data': {
                    'items': items,
                    'total_items': paginator.count,
                    'total_pages': paginator.num_pages,
                    'current_page': page
                }
            }
            
            # Use BuildResponse to return a consistent HTTP response
            response = BuildResponse(response_body).get_response()
            response.status_code = 200  # Set the status code manually
            return response
        
        # Handle invalid request methods
        response = BuildResponse({'error': 'Invalid request method'}).post_response()
        response.status_code = 405  # Set the status code manually
        return response
    
    except Exception as e:
        # Handle exceptions
        response = BuildResponse({'error': str(e)}).post_response()
        response.status_code = 400  # Set the status code manually
        return response

@csrf_exempt
def fetch_product(request, product_id):
    try:
        if request.method == 'GET':
            product = Product.objects.filter(id=product_id).first()
            
            if not product:
                return JsonResponse({'error': 'Product not found'}, status=404)
            
            return JsonResponse({
                'status': True,
                'message': 'Product fetched successfully',
                'data': {
                    'id': product.id,
                    'name': product.name,
                    'quantity': product.quantity,
                    'price': str(product.price),
                    'expiration_date': product.expiration_date,
                    'created_at': product.created_at,
                    'updated_at': product.updated_at
                }
            })
        
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def batch_product(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            items = data.get('items', [])
            
            if not items:
                return JsonResponse({'error': 'No items provided'}, status=400)
            
            results = {}
            
            for item in items:
                operation = item.get('operation', '').upper()
                product_data = item.get('data', {})
                product_id = product_data.get('id')
                
                try:
                    # Validate inputs
                    if operation in ['CREATE', 'UPDATE']:
                        if 'name' in product_data:
                            product_data['name'] = validate_string(product_data['name'], 'name')
                        if 'quantity' in product_data:
                            quantity = validate_number(product_data['quantity'], 'int', 'quantity')
                            if quantity < 0:
                                raise ValueError('Quantity cannot be negative')
                            product_data['quantity'] = quantity
                        if 'price' in product_data:
                            product_data['price'] = validate_number(product_data['price'], 'float', 'price')
                    
                    if operation == 'CREATE':
                        result = Queries(Product).execute_create(product_data)
                        results[f'create_{len(results)}'] = result[0]['status']
                    elif operation == 'UPDATE' and product_id:
                        result = Queries(Product).execute_change(product_data, product_id)
                        results[f'update_{product_id}'] = result[0]['status']
                    else:
                        results[f'invalid_{len(results)}'] = False
                
                except Exception as item_error:
                    results[f'error_{len(results)}'] = str(item_error)
            
            success = EvaluateQueryResults(results).execute_batch_query_results()
            
            return JsonResponse({
                'status': success,
                'message': 'Batch operation completed',
                'results': results
            })
        
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400) 