import uuid
from sqlalchemy import Column, String, Numeric, Text, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("(gen_random_uuid())"))
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    skill = Column(String(50), nullable=False)
    lat = Column(Numeric(9, 6), nullable=False)
    lng = Column(Numeric(9, 6), nullable=False)
    description = Column(Text, nullable=True)
    job_price = Column(Numeric(10, 2), nullable=False)
    platform_fee = Column(Numeric(10, 2), nullable=True)
    status = Column(String(20), nullable=False, default="pending", server_default=text("'pending'"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    citizen = relationship("User", foreign_keys=[citizen_id])
    worker = relationship("User", foreign_keys=[worker_id])
    offers = relationship("BookingOffer", back_populates="booking", cascade="all, delete-orphan")
