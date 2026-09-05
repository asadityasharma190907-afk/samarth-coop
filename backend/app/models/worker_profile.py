import uuid

from sqlalchemy import (
    Boolean,
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


class WorkerProfile(Base):
    __tablename__ = "worker_profiles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("(gen_random_uuid())"),
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    skill = Column(String(50), nullable=False)
    lat = Column(Numeric(9, 6), nullable=False)
    lng = Column(Numeric(9, 6), nullable=False)
    rating = Column(Numeric(2, 1), nullable=True)
    rating_count = Column(Integer, default=0, server_default=text("0"))
    availability = Column(Boolean, default=True, server_default=text("TRUE"))
    verification_status = Column(
        String(20), default="pending", server_default=text("'pending'")
    )
    father_name = Column(String(100), nullable=True)
    date_of_birth = Column(String(20), nullable=True)
    domicile = Column(String(100), nullable=True)
    local_address = Column(String(255), nullable=True)
    marital_status = Column(String(20), nullable=True)
    experience_years = Column(Integer, nullable=True)
    languages_spoken = Column(String(100), nullable=True)
    aadhaar_number = Column(String(12), nullable=True)
    police_verification_status = Column(
        String(20), default="pending", server_default=text("'pending'")
    )
    kyc_payment_status = Column(
        String(20), default="pending", server_default=text("'pending'")
    )
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="worker_profile")
