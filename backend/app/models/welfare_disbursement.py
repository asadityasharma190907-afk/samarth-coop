import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class WelfareDisbursement(Base):
    __tablename__ = "welfare_disbursements"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("(gen_random_uuid())"),
    )
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(30), nullable=False)
    description = Column(Text, nullable=True)
    disbursed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    disbursed_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[disbursed_by])
