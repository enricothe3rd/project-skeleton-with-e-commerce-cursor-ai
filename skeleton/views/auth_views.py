import json
from django.http import JsonResponse
from django.middleware.csrf import get_token
from skeleton.models import User  # You'll need to create this model
from skeleton.utils.queries.validations.core import validate_string


def csrf(request):
    if request.method == 'GET':
        token = get_token(request)
        response = JsonResponse({'csrfToken': token})
        response.set_cookie('csrftoken', token)  # Set CSRF cookie
        return response
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def register(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            
            # Validate inputs
            username = validate_string(data.get('username'), 'username')
            password = validate_string(data.get('password'), 'password')
            email = validate_string(data.get('email'), 'email')
            company_id = validate_string(data.get('company_id'), 'company_id')
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'status': False,
                    'message': 'Username already exists'
                }, status=400)
            
            # Create user
            user = User.objects.create(
                username=username,
                email=email,
                company_id=company_id
            )
            user.set_password(password)
            user.save()
            
            # Generate tokens
            token = user.generate_auth_token()  # You'll need to implement this
            
            response = JsonResponse({
                'status': True,
                'message': 'Registration successful',
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
            
            # Set cookies
            response.set_cookie('token', token)
            response.set_cookie('user_id', user.id)
            response.set_cookie('company_id', company_id)
            
            return response
            
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def login(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            
            username = data.get('username')
            password = data.get('password')
            
            # Validate user
            user = User.objects.filter(username=username).first()
            if not user or not user.check_password(password):
                return JsonResponse({
                    'status': False,
                    'message': 'Invalid credentials'
                }, status=401)
            
            # Generate tokens
            token = user.generate_auth_token()
            csrf_token = get_token(request)
            
            response = JsonResponse({
                'status': True,
                'message': 'Login successful',
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
            
            # Set all cookies with proper settings
            response.set_cookie('csrftoken', csrf_token, httponly=False)
            response.set_cookie('token', token)
            response.set_cookie('user_id', user.id)
            response.set_cookie('company_id', user.company_id)
            
            # Also set CSRF token in header
            response['X-CSRFToken'] = csrf_token
            
            return response
            
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def logout(request):
    try:
        response = JsonResponse({
            'status': True,
            'message': 'Logout successful'
        })
        
        # Remove cookies
        response.delete_cookie('token')
        response.delete_cookie('user_id')
        response.delete_cookie('company_id')
        
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def validate_login(request):
    try:
        # Get token from cookies
        token = request.COOKIES.get('token')
        user_id = request.COOKIES.get('user_id')
        company_id = request.COOKIES.get('company_id')
        
        # Get current CSRF token
        csrf_token = get_token(request)
        
        if not all([token, user_id, company_id]):
            response = JsonResponse({
                'status': False,
                'message': 'Not authenticated',
                'result': False
            }, status=401)
            response.set_cookie('csrftoken', csrf_token, httponly=False)
            return response
            
        response = JsonResponse({
            'status': True,
            'message': 'Valid login',
            'result': True,
            'data': {
                'user_id': user_id,
                'company_id': company_id
            }
        })
        
        # Set all necessary cookies in response
        response.set_cookie('csrftoken', csrf_token, httponly=False)
        response.set_cookie('token', token)
        response.set_cookie('user_id', user_id)
        response.set_cookie('company_id', company_id)
        
        # Also set CSRF token in header
        response['X-CSRFToken'] = csrf_token
        
        return response
        
    except Exception as e:
        # Even in error, set CSRF cookie
        response = JsonResponse({
            'error': str(e),
            'message': 'Authentication failed',
            'result': False
        }, status=401)
        response.set_cookie('csrftoken', get_token(request), httponly=False)
        return response 