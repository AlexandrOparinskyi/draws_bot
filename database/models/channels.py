import enum
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Enum, BigInteger, Constraint, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .users import User
    from .raffles import Raffle


class ChatTypeEnum(enum.Enum):
    CHANNEL = "Channel"
    GROUP = "Group"
    SUPERGROUP = "Supergroup"


class Channel(Base):
    __tablename__ = "channels"

    title: Mapped[str] = mapped_column(String(500), nullable=True)
    username: Mapped[str] = mapped_column(String(500),
                                          nullable=True,
                                          unique=True)
    chat_id: Mapped[int] = mapped_column(BigInteger,
                                         nullable=False,
                                         unique=True)
    type: Mapped[ChatTypeEnum] = mapped_column(Enum(ChatTypeEnum),
                                              nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id",
                   ondelete="cascade"),
        nullable=False
    )
    can_post: Mapped[bool] = mapped_column(default=True, nullable=False)
    can_edit: Mapped[bool] = mapped_column(default=True, nullable=False)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="channels",
        lazy="joined"
    )
    raffle_channels: Mapped[list["RaffleChannel"]] = relationship(
        "RaffleChannel",
        back_populates="channel",
        lazy="selectin"
    )


class RaffleChannel(Base):
    __tablename__ = "raffle_channels"
    __table_args__ = (
        UniqueConstraint("channel_id", "raffle_id", name="uq_id"),
    )

    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"),
                                            nullable=False)
    raffle_id: Mapped[int] = mapped_column(ForeignKey("raffles.id"),
                                           nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    raffle: Mapped["Raffle"] = relationship(
        "Raffle",
        back_populates="raffle_channels"
    )
    channel: Mapped["Channel"] = relationship(
        "Channel",
        back_populates="raffle_channels",
        lazy="selectin"
    )
