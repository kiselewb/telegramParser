from database.db_manager import DBManager
from services.logger import Logger

logger = Logger(__name__).setup_logger()


class ParserDataManager:
    _instance: "ParserDataManager | None" = None
    _parser_data: list
    _include_keywords: list
    _exclude_keywords: list

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = DBManager()
            cls._instance._parser_data = []
            cls._instance._include_keywords = []
            cls._instance._exclude_keywords = []
        return cls._instance

    async def init(self) -> None:
        try:
            await self._load_parser_data()
            await self._load_include_keywords()
            await self._load_exclude_keywords()

            logger.info("✅ ParserDataManager инициализирован")

        except Exception as e:
            logger.error(f"❌ Ошибка инициализации ParserDataManager {e}")
            raise

    def get_include_keywords(self) -> list[str]:
        return self._include_keywords

    async def add_include_keywords(
        self, new_keywords: list[str], parser_data_id: int
    ) -> list[str]:
        new_include_keywords = await self.db.add_include_keywords_for_parser_data(
            new_keywords, parser_data_id
        )

        if new_include_keywords:
            await self.update_all_data()
            return new_include_keywords.keywords

        return []

    async def remove_include_keywords(
        self, keywords_to_remove: list[str], parser_data_id: int
    ) -> list[str]:
        updated = await self.db.delete_include_keywords_for_parser_data(
            keywords_to_remove, parser_data_id
        )

        if updated:
            await self.update_all_data()
            return updated.keywords

        return []

    def get_exclude_keywords(self) -> list[str]:
        return self._exclude_keywords

    async def add_exclude_keywords(self, new_keywords: list[str]) -> list[str]:
        new_exclude_keywords = await self.db.add_exclude_keywords(new_keywords)

        if new_exclude_keywords:
            await self.update_all_data()
            return new_exclude_keywords.keywords

        return []

    async def remove_exclude_keywords(self, keywords_to_remove: list[str]) -> list[str]:
        updated = await self.db.delete_exclude_keywords(keywords_to_remove)

        if updated:
            await self.update_all_data()
            return updated.keywords

        return []

    def get_parser_data(self) -> list[dict[str, str | list]]:
        return self._parser_data

    def get_parser_data_by_id(self, parser_data_id: int) -> dict | None:
        for data in self._parser_data:
            if data["id"] == parser_data_id:
                return data

        return None

    async def update_parser_data_by_id(
        self, data: dict[str, str], parser_data_id: int
    ) -> dict | None:
        new_parser_data = await self.db.update_parser_data(data, id=parser_data_id)

        if new_parser_data:
            await self.update_all_data()

            return {
                "id": new_parser_data.id,
                "category": new_parser_data.category,
                "template": new_parser_data.template,
                "keywords": new_parser_data.keywords,
            }

        return None

    async def _load_parser_data(self) -> None:
        logger.info("Загружаю parser_data из БД")
        parser_data = await self.db.get_all_parser_data()
        self._parser_data = [
            {
                "id": data.id,
                "category": data.category,
                "template": data.template,
                "keywords": data.keywords,
            }
            for data in parser_data
        ]

    async def _load_include_keywords(self) -> None:
        logger.info("Загружаю include_keywords из БД")
        self._include_keywords = [
            keyword.lower()
            for data in self._parser_data
            for keyword in data["keywords"]
        ]

    async def _load_exclude_keywords(self) -> None:
        logger.info("Загружаю exclude_keywords из БД")
        exclude_data = await self.db.get_exclude_parser_data()
        self._exclude_keywords = exclude_data.keywords

    async def update_all_data(self) -> None:
        self._parser_data = []
        self._include_keywords = []
        self._exclude_keywords = []

        await self.init()
