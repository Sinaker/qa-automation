# E-Commerce API - FastAPI Implementation

A complete e-commerce REST API built with FastAPI based on the OpenAPI 3.0 specification. Includes user authentication, product catalog, shopping cart, and order management.

## Features

- **Authentication**: User registration and JWT-based login
- **User Management**: Profile management with address support
- **Product Catalog**: Full CRUD operations with filtering, sorting, and pagination
- **Shopping Cart**: Add, update, remove items with automatic total calculation
- **Order Management**: Place orders, track status, and manage deliveries
- **Admin Features**: Protected endpoints for product and order management

## Technology Stack

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: Secure token-based authentication
- **Bcrypt**: Password hashing
- **SQLite**: Default database (easily configurable for PostgreSQL/MySQL)

## Project Structure

```
API/
├── main.py                 # FastAPI application entry point
├── database.py            # Database configuration and session management
├── models.py              # SQLAlchemy ORM models
├── schemas.py             # Pydantic schemas for request/response validation
├── auth.py                # Authentication utilities (JWT, password hashing)
├── routers/               # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── users.py          # User management endpoints
│   ├── products.py       # Product catalog endpoints
│   ├── cart.py           # Shopping cart endpoints
│   └── orders.py         # Order management endpoints
├── requirements.txt       # Python dependencies
├── openapi.json          # OpenAPI specification
└── README.md             # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone or navigate to the project directory**:
   ```powershell
   cd c:\Users\Kanis\Documents\DOCKER\AI_Testing\Python\API
   ```

2. **Create a virtual environment** (recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure the application** (optional):
   - Edit `auth.py` to change the `SECRET_KEY` for production
   - Edit `database.py` to configure a different database (PostgreSQL, MySQL, etc.)

5. **Run the application**:
   ```powershell
   python main.py
   ```
   
   Or using uvicorn directly:
   ```powershell
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**:
   - API Base URL: http://localhost:8000
   - Interactive API Docs (Swagger UI): http://localhost:8000/docs
   - Alternative API Docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive JWT token

### Users
- `GET /users/{userId}` - Get user by ID (authenticated)
- `PUT /users/{userId}` - Update user information (authenticated)
- `DELETE /users/{userId}` - Delete user account (authenticated)

### Products
- `GET /products` - List all products (with filtering, sorting, pagination)
- `POST /products` - Create a product (admin only)
- `GET /products/{productId}` - Get product by ID
- `PUT /products/{productId}` - Update product (admin only)
- `DELETE /products/{productId}` - Delete product (admin only)

### Cart
- `GET /cart` - Get current user's cart (authenticated)
- `POST /cart` - Add item to cart (authenticated)
- `PUT /cart/items/{itemId}` - Update cart item quantity (authenticated)
- `DELETE /cart/items/{itemId}` - Remove item from cart (authenticated)
- `DELETE /cart` - Clear entire cart (authenticated)

### Orders
- `GET /orders` - List user's orders (authenticated)
- `POST /orders` - Create order from cart (authenticated)
- `GET /orders/{orderId}` - Get order by ID (authenticated)
- `PATCH /orders/{orderId}` - Update order status (admin only)
- `DELETE /orders/{orderId}` - Cancel order (authenticated, pending orders only)

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Register a new user or login to get a JWT token
2. Include the token in the `Authorization` header:
   ```
   Authorization: Bearer <your-token-here>
   ```

### Example Usage

**Register a user**:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "firstName": "John",
    "lastName": "Doe"
  }'
```

**Login**:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Get products**:
```bash
curl -X GET "http://localhost:8000/products?page=1&limit=20&category=electronics"
```

**Add to cart** (authenticated):
```bash
curl -X POST "http://localhost:8000/cart" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "productId": 1,
    "quantity": 2
  }'
```

## Database

By default, the application uses SQLite with a database file named `ecommerce.db` in the project root. The database is automatically created on first run.

### Using PostgreSQL or MySQL

To use PostgreSQL or MySQL, update the `SQLALCHEMY_DATABASE_URL` in `database.py`:

**PostgreSQL**:
```python
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

**MySQL**:
```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```

Don't forget to install the appropriate database driver:
- PostgreSQL: `pip install psycopg2-binary`
- MySQL: `pip install pymysql`

## Admin Users

To create an admin user, you need to manually update the database:

1. Register a user normally
2. Connect to the database and update the `is_admin` field:
   ```sql
   UPDATE users SET is_admin = 1 WHERE email = 'admin@example.com';
   ```

Admin users have access to:
- Create, update, and delete products
- Update order status
- View all orders

## Development

The application runs in development mode with auto-reload enabled by default. Any changes to the code will automatically restart the server.

## Production Deployment

For production deployment:

1. Change the `SECRET_KEY` in `auth.py` to a strong, random value
2. Use a production-grade database (PostgreSQL recommended)
3. Set `reload=False` when running uvicorn
4. Use a process manager like Gunicorn or Supervisor
5. Configure HTTPS/SSL
6. Set up proper CORS policies if needed
7. Implement rate limiting and additional security measures

Example production command:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Testing

You can test the API using:
- Built-in Swagger UI at http://localhost:8000/docs
- Tools like Postman, Insomnia, or curl
- Automated tests (to be implemented)

## License

This is a practice/example project for educational purposes.

## Support

For issues or questions, contact: support@example.com
