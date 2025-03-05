import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Prefetch
from skeleton.models import Order, OrderLine, Product, Customer
from skeleton.utils.general.general import Queries, EvaluateQueryResults
from skeleton.utils.queries.validations.core import validate_number

def format_order_response(order):
    """Helper function to format order response data"""
    order_lines = []
    total_quantity = 0
    
    # Get fresh order data with all related information
    order = Order.objects.select_related('customer').prefetch_related(
        Prefetch(
            'order_lines',
            queryset=OrderLine.objects.select_related('product')
        )
    ).get(id=order.id)
    
    for line in order.order_lines.all():
        order_lines.append({
            'id': line.id,
            'product_id': line.product_id,
            'product_name': line.product.name,
            'quantity': line.quantity,
            'unit_price': str(line.product.price),
            'subtotal': str(line.subtotal)
        })
        total_quantity += line.quantity
    
    return {
        'id': order.id,
        'transaction_code': order.transaction_code,
        'customer': {
            'id': order.customer.id,
            'name': order.customer.name
        },
        'order_summary': {
            'total_items': len(order_lines),
            'total_quantity': total_quantity,
            'order_total': str(order.order_total)
        },
        'order_lines': order_lines,
        'created_at': order.created_at,
        'updated_at': order.updated_at
    }

@csrf_exempt
def create_order(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            
            customer_id = data.get('customer_id')
            order_lines = data.get('order_lines', [])
            
            if not customer_id:
                return JsonResponse({'error': 'Customer ID is required'}, status=400)
            
            if not order_lines:
                return JsonResponse({'error': 'Order lines are required'}, status=400)
            
            # Validate customer exists
            customer = Customer.objects.filter(id=customer_id).first()
            if not customer:
                return JsonResponse({'error': 'Customer not found'}, status=400)
            
            with transaction.atomic():
                # Create order
                order_params = {
                    'customer_id': customer_id,
                    'order_total': 0  # Will be updated after order lines are created
                }
                
                order_result = Queries(Order).execute_create(order_params)
                if not order_result[0]['status']:
                    return JsonResponse({
                        'status': False,
                        'message': order_result[0]['message']
                    }, status=400)
                
                order_id = order_result[0]['values'][0]['id']
                total_amount = 0
                
                # Process order lines
                for line in order_lines:
                    product_id = line.get('product_id')
                    quantity = validate_number(line.get('quantity'), 'int', 'quantity')
                    
                    # Get product and validate quantity
                    product = Product.objects.select_for_update().get(id=product_id)
                    if product.quantity < quantity:
                        transaction.set_rollback(True)
                        return JsonResponse({
                            'status': False,
                            'message': f'Insufficient quantity for product {product.name}'
                        }, status=400)
                    
                    # Calculate subtotal
                    subtotal = product.price * quantity
                    total_amount += subtotal
                    
                    # Create order line
                    line_params = {
                        'order_id': order_id,
                        'product_id': product_id,
                        'quantity': quantity,
                        'subtotal': subtotal
                    }
                    
                    line_result = Queries(OrderLine).execute_create(line_params)
                    if not line_result[0]['status']:
                        transaction.set_rollback(True)
                        return JsonResponse({
                            'status': False,
                            'message': line_result[0]['message']
                        }, status=400)
                    
                    # Update product quantity
                    product.quantity -= quantity
                    product.save()
                
                # Update order total
                order_update = Queries(Order).execute_change(
                    {'order_total': total_amount}, 
                    order_id
                )
                
                if not order_update[0]['status']:
                    transaction.set_rollback(True)
                    return JsonResponse({
                        'status': False,
                        'message': order_update[0]['message']
                    }, status=400)
                
                # Get the created order
                created_order = Order.objects.get(id=order_id)
                
                return JsonResponse({
                    'status': True,
                    'message': 'Order created successfully',
                    'data': format_order_response(created_order)
                })
                
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def update_order(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            order_id = data.get('id')
            order_lines = data.get('order_lines', [])
            
            if not order_id:
                return JsonResponse({'error': 'Order ID is required'}, status=400)
            
            with transaction.atomic():
                # Get existing order
                order = Order.objects.select_for_update().filter(id=order_id).first()
                if not order:
                    return JsonResponse({'error': 'Order not found'}, status=400)
                
                # Get existing order lines
                existing_lines = {
                    line.id: line for line in OrderLine.objects.filter(order_id=order_id)
                }
                
                total_amount = 0
                processed_line_ids = set()
                
                # Process order lines
                for line in order_lines:
                    line_id = line.get('id')
                    product_id = line.get('product_id')
                    quantity = validate_number(line.get('quantity'), 'int', 'quantity')
                    
                    product = Product.objects.select_for_update().get(id=product_id)
                    
                    if line_id and line_id in existing_lines:
                        # Update existing line
                        existing_line = existing_lines[line_id]
                        quantity_diff = quantity - existing_line.quantity
                        
                        if quantity_diff > 0 and product.quantity < quantity_diff:
                            transaction.set_rollback(True)
                            return JsonResponse({
                                'status': False,
                                'message': f'Insufficient quantity for product {product.name}'
                            }, status=400)
                        
                        # Update product quantity
                        product.quantity -= quantity_diff
                        product.save()
                        
                        # Update order line
                        subtotal = product.price * quantity
                        line_params = {
                            'quantity': quantity,
                            'subtotal': subtotal
                        }
                        
                        line_result = Queries(OrderLine).execute_change(line_params, line_id)
                        if not line_result[0]['status']:
                            transaction.set_rollback(True)
                            return JsonResponse({
                                'status': False,
                                'message': line_result[0]['message']
                            }, status=400)
                        
                        total_amount += subtotal
                        processed_line_ids.add(line_id)
                    else:
                        # Create new line
                        if product.quantity < quantity:
                            transaction.set_rollback(True)
                            return JsonResponse({
                                'status': False,
                                'message': f'Insufficient quantity for product {product.name}'
                            }, status=400)
                        
                        subtotal = product.price * quantity
                        line_params = {
                            'order_id': order_id,
                            'product_id': product_id,
                            'quantity': quantity,
                            'subtotal': subtotal
                        }
                        
                        line_result = Queries(OrderLine).execute_create(line_params)
                        if not line_result[0]['status']:
                            transaction.set_rollback(True)
                            return JsonResponse({
                                'status': False,
                                'message': line_result[0]['message']
                            }, status=400)
                        
                        # Update product quantity
                        product.quantity -= quantity
                        product.save()
                        
                        total_amount += subtotal
                
                # Handle removed lines
                for line_id, line in existing_lines.items():
                    if line_id not in processed_line_ids:
                        product = Product.objects.select_for_update().get(id=line.product_id)
                        product.quantity += line.quantity
                        product.save()
                        
                        Queries(OrderLine).execute_unrestricted_delete(line_id)
                
                # Update order total
                order_update = Queries(Order).execute_change(
                    {'order_total': total_amount}, 
                    order_id
                )
                
                if not order_update[0]['status']:
                    transaction.set_rollback(True)
                    return JsonResponse({
                        'status': False,
                        'message': order_update[0]['message']
                    }, status=400)
                
                # Get the updated order
                updated_order = Order.objects.get(id=order_id)
                
                return JsonResponse({
                    'status': True,
                    'message': 'Order updated successfully',
                    'data': format_order_response(updated_order)
                })
                
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def delete_order(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            order_id = data.get('id')
            
            if not order_id:
                return JsonResponse({'error': 'Order ID is required'}, status=400)
            
            with transaction.atomic():
                # Get order lines to restore product quantities
                order_lines = OrderLine.objects.filter(order_id=order_id)
                
                # Restore product quantities
                for line in order_lines:
                    product = Product.objects.select_for_update().get(id=line.product_id)
                    product.quantity += line.quantity
                    product.save()
                
                # Delete order (this will cascade delete order lines)
                result = Queries(Order).execute_unrestricted_delete(order_id)
                
                if result[0]['status']:
                    return JsonResponse({
                        'status': True,
                        'message': 'Order deleted successfully'
                    })
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({
                        'status': False,
                        'message': result[0]['message']
                    }, status=400)
                
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def fetch_orders(request):
    try:
        if request.method == 'GET':
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            search = request.GET.get('search', '')
            
            # Query orders with related data
            orders = Order.objects.select_related('customer').prefetch_related(
                Prefetch(
                    'order_lines',
                    queryset=OrderLine.objects.select_related('product')
                )
            )
            
            if search:
                orders = orders.filter(transaction_code__icontains=search)
            
            # Apply pagination
            paginator = Paginator(orders, page_size)
            current_page = paginator.get_page(page)
            
            # Format response data
            order_data = []
            for order in current_page.object_list:
                order_lines = []
                for line in order.order_lines.all():
                    order_lines.append({
                        'id': line.id,
                        'product_id': line.product_id,
                        'product_name': line.product.name,
                        'quantity': line.quantity,
                        'subtotal': str(line.subtotal)
                    })
                
                order_data.append({
                    'id': order.id,
                    'transaction_code': order.transaction_code,
                    'customer_id': order.customer_id,
                    'customer_name': order.customer.name,
                    'order_total': str(order.order_total),
                    'created_at': order.created_at,
                    'updated_at': order.updated_at,
                    'order_lines': order_lines
                })
            
            return JsonResponse({
                'status': True,
                'message': 'Orders fetched successfully',
                'data': {
                    'items': order_data,
                    'total_items': paginator.count,
                    'total_pages': paginator.num_pages,
                    'current_page': page
                }
            })
        
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def fetch_order(request, order_id):
    try:
        if request.method == 'GET':
            order = Order.objects.select_related('customer').prefetch_related(
                Prefetch(
                    'order_lines',
                    queryset=OrderLine.objects.select_related('product')
                )
            ).filter(id=order_id).first()
            
            if not order:
                return JsonResponse({'error': 'Order not found'}, status=404)
            
            # Format order lines
            order_lines = []
            for line in order.order_lines.all():
                order_lines.append({
                    'id': line.id,
                    'product_id': line.product_id,
                    'product_name': line.product.name,
                    'quantity': line.quantity,
                    'subtotal': str(line.subtotal)
                })
            
            return JsonResponse({
                'status': True,
                'message': 'Order fetched successfully',
                'data': {
                    'id': order.id,
                    'transaction_code': order.transaction_code,
                    'customer_id': order.customer_id,
                    'customer_name': order.customer.name,
                    'order_total': str(order.order_total),
                    'created_at': order.created_at,
                    'updated_at': order.updated_at,
                    'order_lines': order_lines
                }
            })
        
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def batch_order(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            items = data.get('items', [])
            
            if not items:
                return JsonResponse({'error': 'No items provided'}, status=400)
            
            results = {}
            
            with transaction.atomic():
                for item in items:
                    operation = item.get('operation', '').upper()
                    order_data = item.get('data', {})
                    order_id = order_data.get('id')
                    
                    try:
                        if operation == 'CREATE':
                            # Handle order creation
                            customer_id = order_data.get('customer_id')
                            order_lines = order_data.get('order_lines', [])
                            
                            if not customer_id or not order_lines:
                                results[f'create_{len(results)}'] = False
                                continue
                            
                            # Create order
                            order_params = {
                                'customer_id': customer_id,
                                'order_total': 0
                            }
                            
                            order_result = Queries(Order).execute_create(order_params)
                            if not order_result[0]['status']:
                                results[f'create_{len(results)}'] = False
                                continue
                            
                            new_order_id = order_result[0]['values'][0]['id']
                            total_amount = 0
                            
                            # Process order lines
                            for line in order_lines:
                                product_id = line.get('product_id')
                                quantity = validate_number(line.get('quantity'), 'int', 'quantity')
                                
                                product = Product.objects.select_for_update().get(id=product_id)
                                if product.quantity < quantity:
                                    transaction.set_rollback(True)
                                    results[f'create_{len(results)}'] = False
                                    continue
                                
                                subtotal = product.price * quantity
                                total_amount += subtotal
                                
                                line_params = {
                                    'order_id': new_order_id,
                                    'product_id': product_id,
                                    'quantity': quantity,
                                    'subtotal': subtotal
                                }
                                
                                line_result = Queries(OrderLine).execute_create(line_params)
                                if not line_result[0]['status']:
                                    transaction.set_rollback(True)
                                    results[f'create_{len(results)}'] = False
                                    continue
                                
                                product.quantity -= quantity
                                product.save()
                            
                            # Update order total
                            order_update = Queries(Order).execute_change(
                                {'order_total': total_amount}, 
                                new_order_id
                            )
                            
                            results[f'create_{len(results)}'] = order_update[0]['status']
                            
                        elif operation == 'UPDATE' and order_id:
                            # Handle order update
                            order_lines = order_data.get('order_lines', [])
                            
                            order = Order.objects.select_for_update().filter(id=order_id).first()
                            if not order:
                                results[f'update_{order_id}'] = False
                                continue
                            
                            existing_lines = {
                                line.id: line for line in OrderLine.objects.filter(order_id=order_id)
                            }
                            
                            total_amount = 0
                            processed_line_ids = set()
                            
                            # Process order lines
                            for line in order_lines:
                                line_id = line.get('id')
                                product_id = line.get('product_id')
                                quantity = validate_number(line.get('quantity'), 'int', 'quantity')
                                
                                product = Product.objects.select_for_update().get(id=product_id)
                                
                                if line_id and line_id in existing_lines:
                                    # Update existing line
                                    existing_line = existing_lines[line_id]
                                    quantity_diff = quantity - existing_line.quantity
                                    
                                    if quantity_diff > 0 and product.quantity < quantity_diff:
                                        results[f'update_{order_id}'] = False
                                        continue
                                    
                                    product.quantity -= quantity_diff
                                    product.save()
                                    
                                    subtotal = product.price * quantity
                                    line_params = {
                                        'quantity': quantity,
                                        'subtotal': subtotal
                                    }
                                    
                                    line_result = Queries(OrderLine).execute_change(line_params, line_id)
                                    if not line_result[0]['status']:
                                        results[f'update_{order_id}'] = False
                                        continue
                                    
                                    total_amount += subtotal
                                    processed_line_ids.add(line_id)
                                else:
                                    # Create new line
                                    if product.quantity < quantity:
                                        results[f'update_{order_id}'] = False
                                        continue
                                    
                                    subtotal = product.price * quantity
                                    line_params = {
                                        'order_id': order_id,
                                        'product_id': product_id,
                                        'quantity': quantity,
                                        'subtotal': subtotal
                                    }
                                    
                                    line_result = Queries(OrderLine).execute_create(line_params)
                                    if not line_result[0]['status']:
                                        results[f'update_{order_id}'] = False
                                        continue
                                    
                                    product.quantity -= quantity
                                    product.save()
                                    
                                    total_amount += subtotal
                            
                            # Handle removed lines
                            for line_id, line in existing_lines.items():
                                if line_id not in processed_line_ids:
                                    product = Product.objects.select_for_update().get(id=line.product_id)
                                    product.quantity += line.quantity
                                    product.save()
                                    
                                    Queries(OrderLine).execute_unrestricted_delete(line_id)
                            
                            # Update order total
                            order_update = Queries(Order).execute_change(
                                {'order_total': total_amount}, 
                                order_id
                            )
                            
                            results[f'update_{order_id}'] = order_update[0]['status']
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