import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.core.paginator import Paginator
from skeleton.models import Customer
from skeleton.utils.general.general import Queries, EvaluateQueryResults
from skeleton.utils.queries.validations.core import validate_string

@csrf_exempt
def create_customer(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            
            # Validate inputs
            name = validate_string(data.get('name'), 'name')
            address = validate_string(data.get('address'), 'address')
            tin_number = validate_string(data.get('tin_number'), 'tin_number')
            
            params = {
                'name': name,
                'address': address,
                'tin_number': tin_number
            }
            
            result = Queries(Customer).execute_create(params)
            
            if result[0]['status']:
                return JsonResponse({
                    'status': True,
                    'message': 'Customer created successfully',
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
def update_customer(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            customer_id = data.get('id')
            
            if not customer_id:
                return JsonResponse({'error': 'Customer ID is required'}, status=400)
            
            # Validate inputs
            params = {}
            if 'name' in data:
                params['name'] = validate_string(data['name'], 'name')
            if 'address' in data:
                params['address'] = validate_string(data['address'], 'address')
            if 'tin_number' in data:
                params['tin_number'] = validate_string(data['tin_number'], 'tin_number')
            
            result = Queries(Customer).execute_change(params, customer_id)
            
            if result[0]['status']:
                return JsonResponse({
                    'status': True,
                    'message': 'Customer updated successfully',
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
def delete_customer(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            customer_id = data.get('id')
            
            if not customer_id:
                return JsonResponse({'error': 'Customer ID is required'}, status=400)
            
            # Check if customer has existing orders
            customer = Customer.objects.annotate(
                order_count=Count('orders')
            ).filter(id=customer_id).first()
            
            if not customer:
                return JsonResponse({'error': 'Customer not found'}, status=400)
            
            if customer.order_count > 0:
                return JsonResponse({
                    'status': False,
                    'message': 'Cannot delete customer with existing orders'
                }, status=400)
            
            result = Queries(Customer).execute_unrestricted_delete(customer_id)
            
            if result[0]['status']:
                return JsonResponse({
                    'status': True,
                    'message': 'Customer deleted successfully'
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
def fetch_customers(request):
    try:
        if request.method == 'GET':
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            search = request.GET.get('search', '')
            
            # Query customers with optional search
            customers = Customer.objects.all()
            if search:
                customers = customers.filter(name__icontains=search)
            
            # Apply pagination
            paginator = Paginator(customers, page_size)
            current_page = paginator.get_page(page)
            
            return JsonResponse({
                'status': True,
                'message': 'Customers fetched successfully',
                'data': {
                    'items': list(current_page.object_list.values()),
                    'total_items': paginator.count,
                    'total_pages': paginator.num_pages,
                    'current_page': page
                }
            })
        
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def fetch_customer(request, customer_id):
    try:
        if request.method == 'GET':
            customer = Customer.objects.filter(id=customer_id).first()
            
            if not customer:
                return JsonResponse({'error': 'Customer not found'}, status=404)
            
            return JsonResponse({
                'status': True,
                'message': 'Customer fetched successfully',
                'data': {
                    'id': customer.id,
                    'name': customer.name,
                    'address': customer.address,
                    'tin_number': customer.tin_number,
                    'created_at': customer.created_at,
                    'updated_at': customer.updated_at
                }
            })
        
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def batch_customer(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            items = data.get('items', [])
            
            if not items:
                return JsonResponse({'error': 'No items provided'}, status=400)
            
            results = {}
            
            for item in items:
                operation = item.get('operation', '').upper()
                customer_data = item.get('data', {})
                customer_id = customer_data.get('id')
                
                try:
                    # Validate inputs
                    if operation in ['CREATE', 'UPDATE']:
                        if 'name' in customer_data:
                            customer_data['name'] = validate_string(customer_data['name'], 'name')
                        if 'address' in customer_data:
                            customer_data['address'] = validate_string(customer_data['address'], 'address')
                        if 'tin_number' in customer_data:
                            customer_data['tin_number'] = validate_string(customer_data['tin_number'], 'tin_number')
                    
                    if operation == 'CREATE':
                        result = Queries(Customer).execute_create(customer_data)
                        results[f'create_{len(results)}'] = result[0]['status']
                    elif operation == 'UPDATE' and customer_id:
                        result = Queries(Customer).execute_change(customer_data, customer_id)
                        results[f'update_{customer_id}'] = result[0]['status']
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