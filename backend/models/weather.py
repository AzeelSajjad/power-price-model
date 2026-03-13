from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Weather(Base):
    __tablename__ = "weather"
    id: Mapped[String] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column()
    timezone: Mapped[String] = mapped_column()
    temperature: Mapped[int] = mapped_column()
    wind_speed: Mapped[float] = mapped_column()
    cloud_cover: Mapped[float] = mapped_column()