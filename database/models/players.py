from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .users import User
    from .raffles import Raffle


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (
        UniqueConstraint("user_id", "raffle_id", name="ur_id"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",
                                                    ondelete="cascade"),
                                         nullable=False)
    raffle_id: Mapped[int] = mapped_column(ForeignKey("raffles.id",
                                                      ondelete="cascade"),
                                           nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    ref_parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id",
                   ondelete="cascade"),
        nullable=True
    )

    users: Mapped[list["User"]] = relationship("User",
                                               back_populates="players",
                                               lazy="selectin")
    raffles: Mapped[list["Raffle"]] = relationship("Raffle",
                                                   back_populates="players",
                                                   lazy="selectin")
    ref_parent: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="referrals"
    )
