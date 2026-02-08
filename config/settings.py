from pydantic_settings import BaseSettings, SettingsConfigDict
from config.paths import SESSIONS_DIR


class Settings(BaseSettings):
    BOT_TOKEN: str

    API_ID: int
    API_HASH: str
    SESSION_NAME: str = str(SESSIONS_DIR / "bot_session")

    ADMIN_PHONE: str
    ADMIN_PASSWORD: str | None = ""
    ADMIN_ID: list[int] = []

    PARSER_DATA: list[dict[str, str | list]] = [
        {
            "category": "Авито",
            "template": "Это скрипт для пользователя, если он пишет по теме Авито.",
            "keywords": [
                "ищу специалиста по авито",
                "ищу специалиста по настройке рекламы авито",
                "ищу специалиста по авито продвижению",
                "ищу авитолога",
                "настроить авито рекламу",
                "консультация по авито",
                "кто занимается авито",
                "нужна помощь авитолога",
                "нужна помощь по авито",
                "нужна помощь по продвижению авито",
                "нужна помощь по продвижению на авито",
                "кто продвигал на авито",
            ],
        },
        {
            "category": "ВК",
            "template": "Это скрипт для пользователя, если он пишет по теме ВК.",
            "keywords": [
                "ищу специалиста по таргету",
                "ищу специалиста по вк",
                "ищу специалиста по настройке рекламы вк",
                "ищу таргетолога",
                "настроить вк рекламу",
                "настроить вк",
                "консультация по вк",
                "кто занимается вк",
                "кто занимается таргетом",
                "нужна помощь по вк",
                "нужна помощь по продвижению в вк",
                "нужна помощь по продвижению вк",
                "нужна консультация таргетолога",
                "нужна консультация от таргетолога",
                "нужна консультация от спеца по вк",
                "нужна консультация от специалиста по вк",
                "нужна консультация от специалиста по вконтакте",
                "ищем специалиста по вк",
                "ищем таргетолога вк",
                "ищем команду по настройке рекламы в вк",
                "кто делал лиды из вк",
                "кто разбирается в вк",
                "кто продвигал в вк",
            ],
        },
        {
            "category": "Франшизы ВК/Авито",
            "template": "Это скрипт для пользователя, если он пишет по теме франшизы.",
            "keywords": [
                "нужна помощь по продвижению франшиз",
                "нужна помощь по масштабированию франшиз",
                "ищем специалиста по франшизам",
                "ищем команду по масштабированию франшиз",
                "у нас франшиза",
                "у нас франшизный",
                "франшизная сеть",
            ],
        },
    ]

    EXCLUDE_KEYWORDS: list[dict[str, list[str]]] = [
        {
            "keywords": [
                "требуется",
                "в команду",
                "частный",
                "телеграм",
                "директ",
                "яндекс",
                "зп",
                "з/п",
                "ЗП",
                "вакансия",
                "в агентство",
                "по низкой цене",
                "недорого",
                "не дорого",
                "дешево",
            ]
        }
    ]

    LIMIT_COUNT_MESSAGE: int = 20
    LIMIT_WAITING_MESSAGE: int = 3600
    DELAY_SENDING_MESSAGE: int = 30

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
