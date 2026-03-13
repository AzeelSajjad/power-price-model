from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from models.base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime

class Weather(Base):
    __tablename__ = "weather"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column()
    timezone: Mapped[str] = mapped_column()
    temperature: Mapped[int] = mapped_column()
    wind_speed: Mapped[float] = mapped_column()
    cloud_cover: Mapped[float] = mapped_column()