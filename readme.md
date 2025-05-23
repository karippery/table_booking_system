# Table Booking System

A lightweight and robust Table Booking System built with FastAPI and PostgreSQL, designed for restaurants, libraries, cafes, offices, and canteens.

## Features

### Core Functionality
- Real-time table availability checking
- Simple booking management for users
- Admin control panel for system management

### Authentication & Security
- User registration and login (Email & Password)
- OAuth2 with JWT token-based authentication
- Role-based access control (User/Admin)

### User Features
- View available tables in real-time
- Book tables by selecting date/time
- Cancel or modify existing bookings
- View booking history

### Admin Features
- Full CRUD operations for:
  - User management
  - Table management
  - Booking management

### Technical Stack
- **Backend**: FastAPI
- **Database**: PostgreSQL with indexing for performance
- **ORM**: SQLAlchemy with async support
- **Data Validation**: Pydantic
- **API Docs**: Swagger UI included
- **Containerization**: Fully Dockerized


## API Documentation

Interactive API documentation is available at `/docs` when the application is running, powered by Swagger UI.

## Setup & Installation

### Prerequisites
- Docker
- Docker Compose

### Running with Docker

1. Clone the repository
2. Create a `.env` file based on `.env.example`
3. Run:
   ```bash
   docker-compose up --build
   ```
4. Access the API at `http://localhost:8000`

### Without Docker

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL and update DATABASE_URL in `.env`
4. Run:
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage Examples

### User Registration
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

## Frontend Technology 

Stack: React + TypeScript + Vite + Tailwind CSS + TanStack Query + Zustand + React Hook Form + Zod + Axios + React Router + Lucide + React Date Picker
✅ Fast: Vite + Tailwind optimize performance.
✅ Scalable: TanStack Query + Zustand handle growth.
✅ Type-Safe: TypeScript + Zod reduce runtime errors.
✅ Maintainable: Clean structure + modern tooling.

## License

[MIT License](LICENSE)