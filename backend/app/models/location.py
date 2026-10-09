from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(2), unique=True, nullable=False)
    name = Column(String(100), nullable=False)

    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<State(id={self.id}, code={self.code}, name={self.name})>"


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state_id = Column(Integer, ForeignKey("states.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)

    state = relationship("State", back_populates="districts")
    cities = relationship("City", back_populates="district", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("state_id", "name", name="uq_district_state_name"),)

    def __repr__(self):
        return f"<District(id={self.id}, state_id={self.state_id}, name={self.name})>"


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, ForeignKey("districts.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)

    district = relationship("District", back_populates="cities")
    villages = relationship("Village", back_populates="city", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("district_id", "name", name="uq_city_district_name"),)

    def __repr__(self):
        return f"<City(id={self.id}, district_id={self.district_id}, name={self.name}, type={self.type})>"


class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)

    city = relationship("City", back_populates="villages")

    __table_args__ = (UniqueConstraint("city_id", "name", name="uq_village_city_name"),)

    def __repr__(self):
        return f"<Village(id={self.id}, city_id={self.city_id}, name={self.name})>"