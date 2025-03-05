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

- `POST /api/products/create/` - Create a new product
- `POST /api/products/update/` - Update existing product
- `POST /api/products/delete/` - Delete a product
- `GET /api/products/fetch/` - List all products with pagination
- `GET /api/products/fetch/{id}/` - Get single product details
- `POST /api/products/batch/` - Batch operations for products

### Customers

- `POST /api/customers/create/` - Register new customer
- `POST /api/customers/update/` - Update customer details
- `POST /api/customers/delete/` - Delete customer
- `GET /api/customers/fetch/` - List all customers with pagination
- `GET /api/customers/fetch/{id}/` - Get single customer details
- `POST /api/customers/batch/` - Batch operations for customers

### Orders

- `POST /api/orders/create/` - Create new order
- `POST /api/orders/update/` - Update existing order
- `POST /api/orders/delete/` - Delete order
- `GET /api/orders/fetch/` - List all orders with pagination
- `GET /api/orders/fetch/{id}/` - Get single order details
- `POST /api/orders/batch/` - Batch operations for orders

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
// POST /api/orders/create/
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
