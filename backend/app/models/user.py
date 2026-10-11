from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        String(20),
        nullable=False,
    )
    availability = Column(String(255), nullable=True)
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    player_profile = relationship("Player", back_populates="user", uselist=False, cascade="all, delete-orphan")
    coach_profile = relationship("Coach", back_populates="user", uselist=False, cascade="all, delete-orphan")
    club_profile = relationship("Club", back_populates="user", uselist=False, cascade="all, delete-orphan")
    organizer_profile = relationship("Organizer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    referee_profile = relationship("Referee", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, role={self.role})>"


class Player(Base):
    __tablename__ = "players"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(JSON, nullable=True)
    achievements = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="player_profile")
    sport = relationship("Sport")
    position = relationship("Position")
    location = relationship("City")

    def __repr__(self):
        return f"<Player(user_id={self.user_id})>"


class Coach(Base):
    __tablename__ = "coaches"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=True)
    certifications = Column(JSON, nullable=True)
    experience_years = Column(Integer, default=0, nullable=False)
    clubs_coached = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="coach_profile")
    sport = relationship("Sport")

    def __repr__(self):
        return f"<Coach(user_id={self.user_id})>"


class Club(Base):
    __tablename__ = "clubs"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    name = Column(String(255), nullable=False)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    description = Column(Text, nullable=True)
    founded_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="club_profile")
    sport = relationship("Sport")
    location = relationship("City")

    def __repr__(self):
        return f"<Club(user_id={self.user_id}, name={self.name})>"


class Organizer(Base):
    __tablename__ = "organizers"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    organization_name = Column(String(255), nullable=False)
    sports_organized = Column(JSON, nullable=True)
    license_number = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="organizer_profile")

    def __repr__(self):
        return f"<Organizer(user_id={self.user_id}, org={self.organization_name})>"


class Referee(Base):
    __tablename__ = "referees"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=True)
    certification_level = Column(String(50), nullable=True)
    matches_officiated = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="referee_profile")
    sport = relationship("Sport")

    def __repr__(self):
        return f"<Referee(user_id={self.user_id})>"