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
from django.urls import path

from skeleton.utils.queries.products import (
    create_product,
    update_product,
    fetch_products,
    delete_product,
)

from skeleton.utils.queries.customers import (
    create_customer,
    update_customer,
    batch_create_update_customers,
    fetch_customers,
    delete_customer,
)

from skeleton.utils.queries.orders import (
    create_order, fetch_order, fetch_orders, update_order, delete_order
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # Create a new product
    path('product/create_product/', create_product, name='create_product'),

    # Update an existing product by ID
    # http://localhost:8000/update_product/1/
    path('product/update_product/<int:product_id>/', update_product, name='update_product'),

    # Fetch products (single or multiple)
    # "http://localhost:8000/fetch_products/?id=1"
    path('product/fetch_products/', fetch_products, name='fetch_products'),

    # Delete a product by ID
    # http://localhost:8000/delete_product/1/
    path('product/delete_product/<int:product_id>/', delete_product, name='delete_product'),

# Create a new customer
    path('customers/create/', create_customer, name='create_customer'),

    # Update an existing customer
    path('customers/update/<int:customer_id>/', update_customer, name='update_customer'),

    # Batch create or update customers
    path('customers/batch-create-update/', batch_create_update_customers, name='batch_create_update_customers'),

    # Fetch customers (single or multiple)
    path('customers/fetch/', fetch_customers, name='fetch_customers'),

    # Delete a customer
    path('customers/delete/<int:customer_id>/', delete_customer, name='delete_customer'),

# Create an order
    path('orders/create/', create_order, name='create_order'),

    # Fetch a single order
    path('orders/fetch/<int:order_id>/', fetch_order, name='fetch_order'),

    # Fetch multiple orders
    path('orders/fetch/', fetch_orders, name='fetch_orders'),

    # Update an order
    path('orders/update/<int:order_id>/', update_order, name='update_order'),

    # Delete an order
    path('orders/delete/<int:order_id>/', delete_order, name='delete_order'),
]
