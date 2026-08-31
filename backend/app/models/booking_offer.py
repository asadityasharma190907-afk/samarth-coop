import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class BookingOffer(Base):
    __tablename__ = "booking_offers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("(gen_random_uuid())"),
    )
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rank_at_offer = Column(Integer, nullable=False)
    dispatch_score = Column(Numeric(12, 2), nullable=False)
    status = Column(
        String(20), nullable=False, default="offered", server_default=text("'offered'")
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    booking = relationship("Booking", back_populates="offers")
    worker = relationship("User", foreign_keys=[worker_id])
