# Table Booking System

A robust **Table Booking System** built from scratch using **FastAPI** and **PostgreSQL**, designed to handle real-time table reservations, user management, and administrative capabilities.

## Features

- **Authentication & Authorization**:
  - User registration and login (Email & Password).
  - OAuth2 with JWT for secure, token-based authentication.
  - Role-based access control (Users/Admins).

- **Core Functionality**:
  - View available tables in real-time.
  - Book a table by selecting the date and time.
  - Cancel or manage existing bookings.

- **Admin Capabilities**:
  - Manage users (add/remove/modify accounts).
  - Manage tables (update capacities, disable tables for maintenance).

- **API Design**:
  - RESTful API with Swagger documentation.
  - Pydantic for data validation.
  - Proper HTTP status codes for response clarity.

- **Security**:
  - Password hashing using `bcrypt`.
  - Secure JWT token creation with token expiration.
  - Protection against double booking with advisory locks.

- **Database**:
  - PostgreSQL as the database backend.
  - Optimized queries and ACID-compliant transactions.
  - Indexing for high-performance queries.

- **DevOps**:
  - Fully Dockerized application.
  - PostgreSQL health checks.
  - `.env` support for sensitive configuration.

---

## Tech Stack

- **Backend**: FastAPI (Asynchronous)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy with async support
- **Authentication**: OAuth2 + JWT
- **DevOps**: Docker, Docker Compose
- **Validation**: Pydantic

---

## Installation

### Prerequisites
- Python 3.9+
- Docker & Docker Compose

### Steps to Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com/karippery/table_booking_system.git
   cd table_booking_system/app

### Create and configure a .env file:
   ```plaintext
         # Database
         DATABASE_URL=postgresql+asyncpg://postgres:your_secure_password@postgres:5432/booking_db
         POSTGRES_USER=postgres
         POSTGRES_PASSWORD=your_secure_password
         POSTGRES_DB=booking_db

         # Auth
         SECRET_KEY=your_secret_key
         ALGORITHM=HS256
         ACCESS_TOKEN_EXPIRE_MINUTES=30
         REFRESH_TOKEN_EXPIRE_DAYS=7
         PASSWORD_MIN_LENGTH=8

         # Pagination
         PAGINATION_DEFAULT_PAGE_SIZE=25
         PAGINATION_MAX_PAGE_SIZE=100

         # Booking
         DEFAULT_DURATION=4

         #admin
         INITIAL_ADMIN_EMAIL = "admin@admin.com"
         INITIAL_ADMIN_PASSWORD = "Admin123456" 

   ```

1. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

2. Access the API documentation at:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

---

## Usage

### API Endpoints
- **Authentication**:
  - `POST /register`: Register a new user.
  - `POST /token`: Login and get a JWT token.

- **Table Booking**:
  - `GET /tables`: View available tables.
  - `POST /bookings`: Book a table.
  - `DELETE /bookings/{id}`: Cancel a booking.

- **Admin Operations**:
  - `GET /admin/users`: View all users.
  - `POST /admin/tables`: Add or update tables.

---

## Testing

1. Run tests locally with:
   ```bash
   pytest
   ```
2. Use `pytest-asyncio` for testing async endpoints.

---

## Contributions

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Author

Developed by [karippery](https://github.com/karippery).
```
