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

All API endpoints accept and return JSON data. Here's an example of creating an order:

```json
// POST /create_order/
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
```

Response:

```json
{
  "status": true,
  "message": "Order created successfully",
  "data": {
    "id": 1,
    "transaction_code": "TXN12345678",
    "customer": {
      "id": 1,
      "name": "John Doe"
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
        "product_name": "Product A",
        "quantity": 5,
        "unit_price": "19.99",
        "subtotal": "99.95"
      },
      {
        "id": 2,
        "product_id": 2,
        "product_name": "Product B",
        "quantity": 3,
        "unit_price": "33.32",
        "subtotal": "99.97"
      }
    ],
    "created_at": "2024-03-05T12:34:56.789Z",
    "updated_at": "2024-03-05T12:34:56.789Z"
  }
}
```

## Error Handling

The API uses standard HTTP status codes and returns error messages in a consistent format:

```json
{
  "status": false,
  "message": "Error description"
}
```

## License

MIT License
