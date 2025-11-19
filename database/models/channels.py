import enum
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .users import User
    from .raffles import Raffle


class ChannelTypeEnum(enum.Enum):
    SUBSCRIBE = "SUBSCRIBE"
    POST = "POST"


class Channel(Base):
    __tablename__ = "channels"

    url: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id",
                   ondelete="cascade"),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="channels"
    )
    raffles: Mapped[list["Raffle"]] = relationship(
        "Raffle",
        secondary="raffle_channels",
        back_populates="channels"
    )


class RaffleChannel(Base):
    __tablename__ = "raffle_channels"

    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"),
                                            nullable=False)
    raffle_id: Mapped[int] = mapped_column(ForeignKey("raffles.id"),
                                           nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
