from datetime import datetime, timedelta

from fluentogram import TranslatorHub

from config import MAX_RAFFLE_TITLE_LENGTH, MAX_RAFFLE_DESCRIPTION_LENGTH


async def getter_raffle_title(i18n: TranslatorHub,
                              **kwargs) -> dict[str, str]:
    title_text = i18n.raffle.title.text(
        max_symbols=str(MAX_RAFFLE_TITLE_LENGTH)
    )

    return {"title_text": title_text}


async def getter_raffle_description(i18n: TranslatorHub,
                                    **kwargs) -> dict[str, str]:
    description_text = i18n.raffle.description.text(
        max_symbols=str(MAX_RAFFLE_DESCRIPTION_LENGTH)
    )

    return {"description_text": description_text}


async def getter_raffle_media(i18n: TranslatorHub,
                              **kwargs) -> dict[str, str]:
    return {"media_text": i18n.raffle.media.text(),
            "skip_button": i18n.raffle.skip.button()}


async def getter_raffle_end_date(i18n: TranslatorHub,
                                 **kwargs) -> dict[str, str]:
    current_date = datetime.now() + timedelta(hours=1)
    end_date_text = i18n.raffle.end.date.text(
        current_date=current_date.strftime("%d.%m.%Y %H:%M")
    )

    return {"end_date_text": end_date_text}


async def getter_raffle_winners_count(i18n: TranslatorHub,
                                      **kwargs) -> dict[str, str | list]:
    buttons = [i for i in range(1, 6)] + [10]
    return {"winners_count_text": i18n.raffle.winners.text(),
            "buttons": buttons}


async def getter_raffle_ref_system(i18n: TranslatorHub,
                                   **kwargs) -> dict[str, str]:
    return {"ref_system_text": i18n.raffle.ref.system.text(),
            "yes_button": i18n.raffle.ref.system.yes.button(),
            "no_button": i18n.raffle.ref.system.no.button()}
