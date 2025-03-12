"""
URL configuration for structure project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from skeleton.views import product_views, customer_views, order_views, auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Product URLs
    path('create_product/', product_views.create_product, name='create_product'),
    path('update_product/', product_views.update_product, name='update_product'),
    path('delete_product/', product_views.delete_product, name='delete_product'),
    path('fetch_products/', product_views.fetch_products, name='fetch_products'),
    path('fetch_product/<int:product_id>/', product_views.fetch_product, name='fetch_product'),
    path('batch_product/', product_views.batch_product, name='batch_product'),
    
    # Customer URLs
    path('create_customer/', customer_views.create_customer, name='create_customer'),
    path('update_customer/', customer_views.update_customer, name='update_customer'),
    path('delete_customer/', customer_views.delete_customer, name='delete_customer'),
    path('fetch_customers/', customer_views.fetch_customers, name='fetch_customers'),
    path('fetch_customer/<int:customer_id>/', customer_views.fetch_customer, name='fetch_customer'),
    path('batch_customer/', customer_views.batch_customer, name='batch_customer'),
    
    # Order URLs
    path('create_order/', order_views.create_order, name='create_order'),
    path('update_order/', order_views.update_order, name='update_order'),
    path('delete_order/', order_views.delete_order, name='delete_order'),
    path('fetch_orders/', order_views.fetch_orders, name='fetch_orders'),
    path('fetch_order/<int:order_id>/', order_views.fetch_order, name='fetch_order'),
    path('batch_order/', order_views.batch_order, name='batch_order'),
    
    # Auth URLs
    path('csrf/', auth_views.csrf, name='csrf'),
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('users/validate-login', auth_views.validate_login, name='validate_login'),


 ]
