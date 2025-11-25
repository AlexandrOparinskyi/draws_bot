from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

DIR_PATH = 'I18N/locales'


def create_translator_hub() -> TranslatorHub:
    return TranslatorHub(
        {'ru': ('ru', 'en'), 'en': 'en'},
        [
            FluentTranslator(
                locale='ru',
                translator=FluentBundle.from_files(
                    locale='ru',
                    filenames=[f'{DIR_PATH}/ru/general.ftl',
                               f'{DIR_PATH}/ru/user.ftl',
                               f'{DIR_PATH}/ru/raffle.ftl',
                               f'{DIR_PATH}/ru/created_raffle.ftl',
                               f'{DIR_PATH}/ru/channel.ftl',
                               f'{DIR_PATH}/ru/edit_raffle.ftl',
                               f'{DIR_PATH}/ru/player.ftl',]),
            ),
            FluentTranslator(
                locale='en',
                translator=FluentBundle.from_files(
                    locale='en',
                    filenames=[f'{DIR_PATH}/ru/general.ftl',
                               f'{DIR_PATH}/en/user.ftl',
                               f'{DIR_PATH}/en/raffle.ftl',
                               f'{DIR_PATH}/en/created_raffle.ftl',
                               f'{DIR_PATH}/en/edit_raffle.ftl',
                               f'{DIR_PATH}/en/channel.ftl',
                               f'{DIR_PATH}/en/player.ftl', ]),
            ),
        ],
        root_locale='en',
    )
