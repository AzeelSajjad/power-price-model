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

class Price(Base):
    __tablename__ = "Prices"
    id: Mapped[String] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column()
    name: Mapped[String] = mapped_column()
    ptid: Mapped[int] = mapped_column()
    lbmp: Mapped[float] = mapped_column()
    marg_cost_loss: Mapped[float] = mapped_column()
    marg_cost_congestion: Mapped[float] = mapped_column()