from fluentogram import TranslatorHub

from database import Raffle


def get_text_to_watch_raffle(raffle: Raffle,
                              i18n: TranslatorHub) -> str:
    """Create a text to watch raffle for edit"""
    date = raffle.end_date.strftime("%d.%m.%Y")
    time = raffle.end_date.strftime("%H:%M")

    text = (f"{raffle.title}\n\n"
            f"{raffle.description}\n"
            f"Розыгрыш закончится {date} в {time}")

    return text
