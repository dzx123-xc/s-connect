from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Sport(Base):
    __tablename__ = "sports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    icon = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    positions = relationship("Position", back_populates="sport", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sport(id={self.id}, name={self.name}, slug={self.slug})>"


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sport_id = Column(Integer, ForeignKey("sports.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(10), nullable=True)

    sport = relationship("Sport", back_populates="positions")

    def __repr__(self):
        return f"<Position(id={self.id}, sport_id={self.sport_id}, name={self.name})>"