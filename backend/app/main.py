from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    admin,
    auth,
    bookings,
    enterprise,
    federation,
    kyc,
    offers,
    wallet,
    welfare,
    workers,
)

app = FastAPI(
    title="Samarth API",
    description="Cooperative Gig Services Platform API",
    version="1.0.0",
)

# Enable CORS for frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(kyc.router, prefix="/kyc", tags=["KYC"])
app.include_router(workers.router, prefix="/workers", tags=["Workers"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(offers.router, prefix="/booking-offers", tags=["Offers"])
app.include_router(wallet.router, prefix="/wallet", tags=["Wallet"])
app.include_router(welfare.router, prefix="/welfare-fund", tags=["Welfare Fund"])
app.include_router(federation.router, prefix="/federation", tags=["Federation"])
app.include_router(enterprise.router, prefix="/enterprise", tags=["Enterprise"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
