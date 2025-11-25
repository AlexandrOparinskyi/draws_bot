from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .raffles import RaffleTypeEnum

if TYPE_CHECKING:
    from .raffles import Raffle
    from .channels import Channel
    from .players import RafflePlayer


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str | None]

    is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)

    raffles: Mapped[list["Raffle"]] = relationship("Raffle",
                                                   back_populates="user",
                                                   lazy="selectin")
    channels: Mapped[list["Channel"]] = relationship("Channel",
                                                     back_populates="user",
                                                     lazy="selectin")
    raffle_players: Mapped[list["RafflePlayer"]] = relationship(
        "RafflePlayer",
        back_populates="users",
        lazy="selectin"
    )

    @property
    def created_raffles(self) -> list["Raffle"]:
        return [r for r in self.raffles
                if r.raffle_type == RaffleTypeEnum.CREATED]

    @property
    def active_raffles(self) -> list["Raffle"]:
        return [r for r in self.raffles
                if r.raffle_type == RaffleTypeEnum.ACTIVE]

    @property
    def completed_raffles(self)-> list["Raffle"]:
        return [r for r in self.raffles
                if r.raffle_type == RaffleTypeEnum.COMPLETED]

    @property
    def play_raffles(self) -> list["Raffle"]:
        return [rp.raffles for rp in self.raffle_players]
