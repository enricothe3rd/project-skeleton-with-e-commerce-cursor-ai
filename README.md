# E-Commerce System API

A Django-based REST API for managing an e-commerce system with Product, Customer, and Order management capabilities.

## Features

- **Product Management**

  - Create, read, update, and delete products
  - Batch operations for products
  - Search and pagination support

- **Customer Management**

  - Customer registration and profile management
  - Customer search and listing
  - Batch operations for customers

- **Order Management**
  - Create and process orders
  - Order history and tracking
  - Detailed order information with product details
  - Batch order processing
  - Transaction management and inventory control

## API Endpoints

### Products

- `POST /create_product/` - Create a new product
- `POST /update_product/` - Update existing product
- `POST /delete_product/` - Delete a product
- `GET /fetch_products/` - List all products with pagination
- `GET /fetch_product/{product_id}/` - Get single product details
- `POST /batch_product/` - Batch operations for products

### Customers

- `POST /create_customer/` - Register new customer
- `POST /update_customer/` - Update customer details
- `POST /delete_customer/` - Delete customer
- `GET /fetch_customers/` - List all customers with pagination
- `GET /fetch_customer/{customer_id}/` - Get single customer details
- `POST /batch_customer/` - Batch operations for customers

### Orders

- `POST /create_order/` - Create new order
- `POST /update_order/` - Update existing order
- `POST /delete_order/` - Delete order
- `GET /fetch_orders/` - List all orders with pagination
- `GET /fetch_order/{order_id}/` - Get single order details
- `POST /batch_order/` - Batch operations for orders

## Setup

1. Clone the repository

```bash
git clone <repository-url>
```

2. Create and activate virtual environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run migrations

```bash
python manage.py migrate
```

5. Start the development server

```bash
python manage.py runserver
```

## API Documentation

### Request/Response Format

All API endpoints accept and return JSON data. Below are examples for each endpoint:

### Product Endpoints

#### Create Product

```json
// POST /create_product/
Request:
{
    "name": "Gaming Laptop",
    "quantity": 50,
    "price": "1299.99",
    "expiration_date": "2025-12-31"  // Optional
}

Response:
{
    "status": true,
    "message": "Product created successfully",
    "data": {
        "id": 1,
        "name": "Gaming Laptop",
        "quantity": 50,
        "price": "1299.99",
        "expiration_date": "2025-12-31",
        "created_at": "2024-03-05T12:34:56.789Z",
        "updated_at": "2024-03-05T12:34:56.789Z"
    }
}
```

#### Update Product

```json
// POST /update_product/
Request:
{
    "id": 1,
    "name": "Gaming Laptop Pro",
    "quantity": 45,
    "price": "1399.99",
    "expiration_date": "2025-12-31"
}

Response:
{
    "status": true,
    "message": "Product updated successfully",
    "data": {
        "id": 1,
        "name": "Gaming Laptop Pro",
        "quantity": 45,
        "price": "1399.99",
        "expiration_date": "2025-12-31",
        "created_at": "2024-03-05T12:34:56.789Z",
        "updated_at": "2024-03-05T13:00:00.000Z"
    }
}
```

#### Delete Product

```json
// POST /delete_product/
Request:
{
    "id": 1
}

Response:
{
    "status": true,
    "message": "Product deleted successfully"
}
```

#### Fetch Products

```json
// GET /fetch_products/?page=1&page_size=10&search=laptop
Response:
{
    "status": true,
    "message": "Products fetched successfully",
    "data": {
        "items": [
            {
                "id": 1,
                "name": "Gaming Laptop Pro",
                "quantity": 45,
                "price": "1399.99",
                "expiration_date": "2025-12-31",
                "created_at": "2024-03-05T12:34:56.789Z",
                "updated_at": "2024-03-05T13:00:00.000Z"
            }
        ],
        "total_items": 1,
        "total_pages": 1,
        "current_page": 1
    }
}
```

#### Fetch Single Product

```json
// GET /fetch_product/1/
Response:
{
    "status": true,
    "message": "Product fetched successfully",
    "data": {
        "id": 1,
        "name": "Gaming Laptop Pro",
        "quantity": 45,
        "price": "1399.99",
        "expiration_date": "2025-12-31",
        "created_at": "2024-03-05T12:34:56.789Z",
        "updated_at": "2024-03-05T13:00:00.000Z"
    }
}
```

#### Batch Product Operations

```json
// POST /batch_product/
Request:
{
    "items": [
        {
            "operation": "CREATE",
            "data": {
                "name": "New Product",
                "quantity": 100,
                "price": "99.99"
            }
        },
        {
            "operation": "UPDATE",
            "data": {
                "id": 1,
                "name": "Updated Product",
                "quantity": 50,
                "price": "149.99"
            }
        }
    ]
}

Response:
{
    "status": true,
    "message": "Batch operation completed",
    "results": {
        "create_0": true,
        "update_1": true
    }
}
```

### Customer Endpoints

#### Create Customer

```json
// POST /create_customer/
Request:
{
    "name": "John Doe",
    "address": "123 Main St, City, Country",
    "tin_number": "123-456-789-000"
}

Response:
{
    "status": true,
    "message": "Customer created successfully",
    "data": {
        "id": 1,
        "name": "John Doe",
        "address": "123 Main St, City, Country",
        "tin_number": "123-456-789-000",
        "created_at": "2024-03-05T12:34:56.789Z",
        "updated_at": "2024-03-05T12:34:56.789Z"
    }
}
```

#### Update Customer

```json
// POST /update_customer/
Request:
{
    "id": 1,
    "name": "John Doe Jr",
    "address": "456 New St, City, Country",
    "tin_number": "123-456-789-000"
}

Response:
{
    "status": true,
    "message": "Customer updated successfully",
    "data": {
        "id": 1,
        "name": "John Doe Jr",
        "address": "456 New St, City, Country",
        "tin_number": "123-456-789-000",
        "created_at": "2024-03-05T12:34:56.789Z",
        "updated_at": "2024-03-05T13:00:00.000Z"
    }
}
```

#### Delete Customer

```json
// POST /delete_customer/
Request:
{
    "id": 1
}

Response:
{
    "status": true,
    "message": "Customer deleted successfully"
}
```

#### Fetch Customers

```json
// GET /fetch_customers/?page=1&page_size=10&search=john
Response:
{
    "status": true,
    "message": "Customers fetched successfully",
    "data": {
        "items": [
            {
                "id": 1,
                "name": "John Doe Jr",
                "address": "456 New St, City, Country",
                "tin_number": "123-456-789-000",
                "created_at": "2024-03-05T12:34:56.789Z",
                "updated_at": "2024-03-05T13:00:00.000Z"
            }
        ],
        "total_items": 1,
        "total_pages": 1,
        "current_page": 1
    }
}
```

#### Fetch Single Customer

```json
// GET /fetch_customer/1/
Response:
{
    "status": true,
    "message": "Customer fetched successfully",
    "data": {
        "id": 1,
        "name": "John Doe Jr",
        "address": "456 New St, City, Country",
        "tin_number": "123-456-789-000",
        "created_at": "2024-03-05T12:34:56.789Z",
        "updated_at": "2024-03-05T13:00:00.000Z"
    }
}
```

#### Batch Customer Operations

```json
// POST /batch_customer/
Request:
{
    "items": [
        {
            "operation": "CREATE",
            "data": {
                "name": "Jane Doe",
                "address": "789 Oak St, City, Country",
                "tin_number": "987-654-321-000"
            }
        },
        {
            "operation": "UPDATE",
            "data": {
                "id": 1,
                "name": "John Doe III",
                "address": "456 New St, City, Country",
                "tin_number": "123-456-789-000"
            }
        }
    ]
}

Response:
{
    "status": true,
    "message": "Batch operation completed",
    "results": {
        "create_0": true,
        "update_1": true
    }
}
```

### Order Endpoints

#### Create Order

```json
// POST /create_order/
Request:
{
    "customer_id": 1,
    "order_lines": [
        {
            "product_id": 1,
            "quantity": 5
        },
        {
            "product_id": 2,
            "quantity": 3
        }
    ]
}

Response:
{
    "status": true,
    "message": "Order created successfully",
    "data": {
        "id": 1,
        "transaction_code": "TXN12345678",
        "customer": {
            "id": 1,
            "name": "John Doe Jr"
        },
        "order_summary": {
            "total_items": 2,
            "total_quantity": 8,
            "order_total": "199.92"
        },
        "order_lines": [
            {
                "id": 1,
                "product_id": 1,
                "product_name": "Gaming Laptop Pro",
                "quantity": 5,
                "unit_price": "1399.99",
                "subtotal": "6999.95"
            },
            {
                "id": 2,
                "product_id": 2,
                "product_name": "Gaming Mouse",
                "quantity": 3,
                "unit_price": "59.99",
                "subtotal": "179.97"
            }
        ],
        "created_at": "2024-03-05T12:34:56.789Z",
        "updated_at": "2024-03-05T12:34:56.789Z"
    }
}
```

#### Update Order

```json
// POST /update_order/
Request:
{
    "id": 1,
    "order_lines": [
        {
            "id": 1,
            "product_id": 1,
            "quantity": 6
        },
        {
            "product_id": 3,
            "quantity": 2
        }
    ]
}

Response:
{
    "status": true,
    "message": "Order updated successfully",
    "data": {
        "id": 1,
        "transaction_code": "TXN12345678",
        "customer": {
            "id": 1,
            "name": "John Doe Jr"
        },
        "order_summary": {
            "total_items": 2,
            "total_quantity": 8,
            "order_total": "8599.92"
        },
        "order_lines": [
            {
                "id": 1,
                "product_id": 1,
                "product_name": "Gaming Laptop Pro",
                "quantity": 6,
                "unit_price": "1399.99",
                "subtotal": "8399.94"
            },
            {
                "id": 3,
                "product_id": 3,
                "product_name": "Gaming Headset",
                "quantity": 2,
                "unit_price": "99.99",
                "subtotal": "199.98"
            }
        ],
        "created_at": "2024-03-05T12:34:56.789Z",
        "updated_at": "2024-03-05T13:00:00.000Z"
    }
}
```

#### Delete Order

```json
// POST /delete_order/
Request:
{
    "id": 1
}

Response:
{
    "status": true,
    "message": "Order deleted successfully"
}
```

#### Fetch Orders

```json
// GET /fetch_orders/?page=1&page_size=10&search=TXN123
Response:
{
    "status": true,
    "message": "Orders fetched successfully",
    "data": {
        "items": [
            {
                "id": 1,
                "transaction_code": "TXN12345678",
                "customer_id": 1,
                "customer_name": "John Doe Jr",
                "order_total": "8599.92",
                "created_at": "2024-03-05T12:34:56.789Z",
                "updated_at": "2024-03-05T13:00:00.000Z",
                "order_lines": [
                    {
                        "id": 1,
                        "product_id": 1,
                        "product_name": "Gaming Laptop Pro",
                        "quantity": 6,
                        "subtotal": "8399.94"
                    },
                    {
                        "id": 3,
                        "product_id": 3,
                        "product_name": "Gaming Headset",
                        "quantity": 2,
                        "subtotal": "199.98"
                    }
                ]
            }
        ],
        "total_items": 1,
        "total_pages": 1,
        "current_page": 1
    }
}
```

#### Fetch Single Order

```json
// GET /fetch_order/1/
Response:
{
    "status": true,
    "message": "Order fetched successfully",
    "data": {
        "id": 1,
        "transaction_code": "TXN12345678",
        "customer_id": 1,
        "customer_name": "John Doe Jr",
        "order_total": "8599.92",
        "created_at": "2024-03-05T12:34:56.789Z",
        "updated_at": "2024-03-05T13:00:00.000Z",
        "order_lines": [
            {
                "id": 1,
                "product_id": 1,
                "product_name": "Gaming Laptop Pro",
                "quantity": 6,
                "subtotal": "8399.94"
            },
            {
                "id": 3,
                "product_id": 3,
                "product_name": "Gaming Headset",
                "quantity": 2,
                "subtotal": "199.98"
            }
        ]
    }
}
```

#### Batch Order Operations

```json
// POST /batch_order/
Request:
{
    "items": [
        {
            "operation": "CREATE",
            "data": {
                "customer_id": 1,
                "order_lines": [
                    {
                        "product_id": 1,
                        "quantity": 2
                    }
                ]
            }
        },
        {
            "operation": "UPDATE",
            "data": {
                "id": 1,
                "order_lines": [
                    {
                        "id": 1,
                        "product_id": 1,
                        "quantity": 7
                    }
                ]
            }
        }
    ]
}

Response:
{
    "status": true,
    "message": "Batch operation completed",
    "results": {
        "create_0": true,
        "update_1": true
    }
}
```

## Error Handling

The API uses standard HTTP status codes and returns error messages in a consistent format:

```json
{
  "status": false,
  "message": "Error description",
  "error": "Detailed error message or validation errors"
}
```

Common error scenarios:

```json
// 400 Bad Request - Invalid data
{
    "status": false,
    "message": "Invalid request data",
    "error": "Quantity must be a positive integer"
}

// 404 Not Found
{
    "status": false,
    "message": "Resource not found",
    "error": "Product with ID 999 does not exist"
}

// 400 Bad Request - Insufficient stock
{
    "status": false,
    "message": "Operation failed",
    "error": "Insufficient quantity for product Gaming Laptop Pro"
}
```

## License

MIT License
