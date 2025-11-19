import enum
from datetime import datetime
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users import User

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Raffle(Base):
    __tablename__ = "raffles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",
                                                    ondelete="cascade"),
                                         nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1500), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(100),
                                                     nullable=True)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    winners_count: Mapped[int] = mapped_column(nullable=False)
    ref_system: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    photo_id: Mapped[str] = mapped_column(String(100), nullable=True)
    video_id: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="raffles")
    channels: Mapped[list["Channel"]] = relationship("Channel",
                                                     back_populates="raffle",
                                                     lazy="selectin")


class ChannelTypeEnum(enum.Enum):
    SUBSCRIBE = "SUBSCRIBE"
    POST = "POST"


class Channel(Base):
    __tablename__ = "channels"

    url: Mapped[str] = mapped_column(String(200), nullable=False)
    raffle_id: Mapped[int] = mapped_column(ForeignKey("raffles.id",
                                                      ondelete="cascade"),
                                           nullable=False)

    raffle: Mapped["Raffle"] = relationship("Raffle",
                                            back_populates="channels")
