
### **1. What We're Building**
A **Restaurant Table Booking System** with:
- User authentication (signup/login)
- Table management (20 tables with different capacities)
- Booking management (create/view/cancel bookings)
- Admin capabilities (user management, table management)

### **2. How It Works**
**System Flow:**
1. Users register/login via authentication endpoints
2. Authenticated users can:
   - Check table availability by time/date/party size
   - Book available tables
   - View/cancel their bookings
3. Database maintains:
   - User credentials (hashed passwords)
   - Table inventory
   - Booking records with time slots

### **3. User Actions**
| Action | Endpoint | Method |
|--------|----------|--------|
| Register | `/auth/register` | POST |
| Login | `/auth/token` | POST |
| Check availability | `/bookings/availability` | GET |
| Create booking | `/bookings` | POST |
| View bookings | `/bookings` | GET |
| Cancel booking | `/bookings/{id}` | DELETE |

### **4. Key API Endpoints**
```mermaid
graph TD
    A[Auth] --> B[/register POST]
    A --> C[/login POST]
    D[Bookings] --> E[/availability GET]
    D --> F[/bookings POST]
    D --> G[/bookings GET]
    D --> H[/bookings/{id} DELETE]
```

### **5. Technology Stack**
| Category | Technology |
|----------|------------|
| Framework | FastAPI (Python) |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async) |
| Authentication | OAuth2 + JWT |
| Containerization | Docker |
| Documentation | Swagger UI/ReDoc |
| Testing | Pytest |

### **6. Key Features Implemented**
1. **Security**:
   - Password hashing (bcrypt)
   - JWT token authentication
   - Role-based access control

2. **Database**:
   - Optimized queries with indexes
   - Advisory locks for concurrent bookings
   - ACID-compliant transactions

3. **API Design**:
   - RESTful endpoints
   - Pydantic validation
   - Proper HTTP status codes

4. **DevOps**:
   - Dockerized application
   - PostgreSQL health checks
   - Environment variables

### **7. Sample Workflow**
1. User registers → gets JWT token
2. Searches for available tables (6pm, 4 people)
3. Books a table → system checks availability
4. Receives confirmation with booking ID
5. Can view/cancel booking later

### **8. Special Considerations**
- Prevents double-booking with database locks
- Validates booking times (no past dates)
- Rate limiting on booking endpoints
- Email notifications (can be added)

### **9. How to Run**
```bash
# With Docker (recommended)
docker compose up --build

# Manually
uvicorn app.main:app --reload
```
Access docs at `http://localhost:8000/docs`

This system provides a complete, production-ready table reservation system following modern API best practices with proper security and scalability considerations.

## Project structure

        table_booking_system/
        ├── .env                    # Environment variables
        ├── docker-compose.yml      # Docker compose configuration
        ├── Dockerfile              # Docker image setup
        ├── requirements.txt        # Python dependencies
        │
        ├── app/                    # Main application code
        │   ├── __init__.py         # Makes app a Python package
        │   ├── main.py             # FastAPI app entry point
        │   ├── database.py         # Database connection setup
        │   ├── models.py           # SQLAlchemy models (User, Table, Booking)
        │   │
        │   ├── schemas/            # Pydantic models
        │   │   ├── __init__.py
        │   │   ├── user.py         # User schemas (UserCreate, UserResponse)
        │   │   └── booking.py      # Booking schemas (BookingCreate, BookingResponse)
        │   │
        │   ├── crud/               # Database operations
        │   │   ├── __init__.py
        │   │   ├── user.py         # User CRUD operations
        │   │   └── booking.py      # Booking CRUD operations
        │   │
        │   ├── utils/              # Utility functions
        │   │   ├── __init__.py
        │   │   ├── security.py     # Password hashing, JWT
        │   │   └── token.py        # Token handling
        │   │
        │   └── api/
        │       ├── __init__.py
        │       └── endpoints/      # API route handlers
        │           ├── __init__.py
        │           ├── auth.py     # Authentication routes
        │           └── booking.py  # Booking routes
        │
        ├── venv/                   # Virtual environment (ignored in Git)
        │
        └── tests/                  # Test files (optional)
            ├── __init__.py
            ├── test_auth.py
            └── test_booking.py