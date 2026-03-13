from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from models.base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime


class Price(Base):
    __tablename__ = "prices"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column()
    name: Mapped[str] = mapped_column()
    ptid: Mapped[int] = mapped_column()
    lbmp: Mapped[float] = mapped_column()
    marg_cost_loss: Mapped[float] = mapped_column()
    marg_cost_congestion: Mapped[float] = mapped_column()