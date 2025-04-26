from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoint import auth, booking, table
from app.database import engine, Base
from app.initial_data import create_admin_user
from app.utils.token import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        await create_admin_user()
    except Exception as e:
        print(f"Failed to create admin user: {e}")
        # Consider whether to continue startup or raise

    yield

app = FastAPI(
    lifespan=lifespan,
    title="Table Booking API",
    description=(
        "API for managing table bookings in a restaurant, library, or "
        "similar venue."
    ),
    version="1.0.0",
    swagger_ui_parameters={
        "oauth2RedirectUrl": "/docs/oauth2-redirect",
    }
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(
    table.router,
    prefix="/tables",
    tags=["tables"]
)
app.include_router(
    booking.router,
    prefix="/bookings",
    tags=["bookings"],
    dependencies=[Depends(get_current_user)]
)


@app.get("/")
async def root():
    return {"message": "Restaurant Booking System"}