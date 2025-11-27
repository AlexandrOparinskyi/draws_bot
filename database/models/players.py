from typing import Optional
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .raffles import Raffle
    from .users import User


class RafflePlayer(Base):
    __tablename__ = "raffle_players"
    __table_args__ = (
        UniqueConstraint("user_id", "raffle_id", name="p_uq_id"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",
                                                    ondelete="cascade"),
                                         nullable=False)
    raffle_id: Mapped[int] = mapped_column(ForeignKey("raffles.id",
                                                      ondelete="cascade"),
                                           nullable=False)
    ref_parent: Mapped[Optional[int]] = mapped_column(BigInteger,
                                                      nullable=True)
    place: Mapped[Optional[int]] = mapped_column(nullable=True)


    user: Mapped["User"] = relationship(
        "User",
        back_populates="raffle_players",
        lazy="selectin"
    )
    raffle: Mapped["Raffle"] = relationship(
        "Raffle",
        back_populates="raffle_players",
        lazy="selectin"
    )
