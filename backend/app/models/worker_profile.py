import uuid
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class WorkerProfile(Base):
    __tablename__ = "worker_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("(gen_random_uuid())"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    skill = Column(String(50), nullable=False)
    lat = Column(Numeric(9, 6), nullable=False)
    lng = Column(Numeric(9, 6), nullable=False)
    rating = Column(Numeric(2, 1), nullable=True)
    availability = Column(Boolean, default=True, server_default=text("TRUE"))
    verified = Column(Boolean, default=False, server_default=text("FALSE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="worker_profile")
