import enum
from datetime import datetime
from typing import Optional
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .users import User
    from .channels import Channel


class RaffleTypeEnum(enum.Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class Raffle(Base):
    __tablename__ = "raffles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id",
                   ondelete="cascade"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1500), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    winners_count: Mapped[int] = mapped_column(nullable=False)
    ref_system: Mapped[bool] = mapped_column(default=False, nullable=False)
    raffle_type: Mapped[RaffleTypeEnum] = mapped_column(
        Enum(RaffleTypeEnum),
        default=RaffleTypeEnum.CREATED,
        nullable=False
    )
    photo_id: Mapped[str] = mapped_column(String(100), nullable=True)
    video_id: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="raffles")
    channels: Mapped[list["Channel"]] = relationship(
        "Channel",
        secondary="raffle_channels",
        back_populates="raffles"
    )
