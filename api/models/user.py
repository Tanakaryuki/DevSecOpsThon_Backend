from sqlalchemy import func, Column,String, Boolean, DateTime, String
from sqlalchemy.orm import relationship
from api.db import Base, generate_uuid


class User(Base):
    __tablename__ = "Users"

    uuid = Column(String(48), default=generate_uuid,
                  primary_key=True, index=True)
    username = Column(String(48), unique=True, nullable=False, index=True)
    hashed_password = Column(String(96), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())