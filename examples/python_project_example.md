# Python Project Example - Web App Development

This example shows how to use LogSec for tracking a Python web application development project.

## Project: E-Commerce API

### Session 1: Initial Setup
```python
lo_save("""
# E-Commerce API Project Started

## Tech Stack Decided:
- FastAPI for the API framework
- PostgreSQL for database
- SQLAlchemy for ORM
- Alembic for migrations
- JWT for authentication

## Initial Structure:
```
ecommerce_api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── routes/
│   └── services/
├── tests/
├── requirements.txt
└── .env.example
```

STATUS: Project scaffolding complete
NEXT: Create database models for User, Product, Order
""", "ecommerce_api")
```

### Session 2: Database Models
```python
lo_save("""
# Database Models Implementation

Created core models:

1. **User Model** (models/user.py):
   - id, email, password_hash
   - created_at, updated_at
   - is_active, is_admin

2. **Product Model** (models/product.py):
   - id, name, description
   - price, stock_quantity
   - category_id, created_at

3. **Order Model** (models/order.py):
   - id, user_id, total_amount
   - status (pending, paid, shipped, delivered)
   - created_at, updated_at

STATUS: Database models complete
POSITION: models/order.py:45 - working on OrderItem relationship
NEXT: Create Alembic migrations
PROBLEM: Need to handle decimal precision for prices
""", "ecommerce_api")
```

### Session 3: API Endpoints
```python
lo_save("""
# API Endpoints Implementation

## Completed Endpoints:

### Authentication
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- GET /auth/me

### Products
- GET /products (with pagination)
- GET /products/{id}
- POST /products (admin only)
- PUT /products/{id} (admin only)
- DELETE /products/{id} (admin only)

### Orders
- GET /orders (user's orders)
- POST /orders
- GET /orders/{id}
- PUT /orders/{id}/status (admin only)

STATUS: Core API endpoints functional
POSITION: routes/orders.py:78 - implementing order status webhooks
NEXT: Add input validation with Pydantic schemas
TODO: 
- Add rate limiting
- Implement caching for product listings
- Add comprehensive error handling
""", "ecommerce_api")
```

### Searching Your Knowledge Base

```python
# Find all sessions about authentication
results = lo_load("ecommerce_api", "authentication JWT")

# Find database-related work
results = lo_load("ecommerce_api", "database models schema")

# Find debugging sessions
results = lo_load("ecommerce_api", "error problem bug")
```

### Continuing Work

```python
# Get back to where you left off
context = lo_start("ecommerce_api")

# This will show:
# - Last position: routes/orders.py:78
# - Next steps: Add input validation
# - Active files you were working on
# - Any problems you were debugging
```

## Best Practices Demonstrated

1. **Structured Status Updates**: Always include STATUS, POSITION, NEXT
2. **Problem Documentation**: Note any issues for future reference
3. **Code Context**: Include relevant code structure/snippets
4. **TODO Tracking**: Keep track of pending tasks
5. **Technical Details**: Document decisions and rationale

## Knowledge Type Classification

LogSec automatically classified these sessions:
- Session 1: `architecture` (system design, tech stack)
- Session 2: `schema` (database models)
- Session 3: `implementation` (API endpoints)

This helps with targeted searches later!
