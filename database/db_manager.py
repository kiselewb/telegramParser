from typing import Sequence

from sqlalchemy import select, insert, update, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config.settings import settings
from database.models import Message, ProcessedMessage, ParserData, ExcludeParserData


class DBManager:
    _instance: "DBManager | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.engine = create_async_engine(
                settings.DATABASE_URL, echo=False
            )
            cls._instance.async_session = async_sessionmaker(
                cls._instance.engine, expire_on_commit=False
            )
        return cls._instance

    async def save_data_message(self, data: dict):
        async with self.async_session() as session:
            stmt = insert(Message).values(**data)
            await session.execute(stmt)
            await session.commit()

    async def save_processed_message(self, data: dict) -> ProcessedMessage | None:
        async with self.async_session() as session:
            stmt = insert(ProcessedMessage).values(**data).returning(ProcessedMessage)
            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one_or_none()

    async def get_processed_message(self, **filter_by) -> ProcessedMessage | None:
        async with self.async_session() as session:
            query = select(ProcessedMessage).filter_by(**filter_by)
            result = await session.execute(query)

            return result.scalar_one_or_none()

    async def update_processed_message(self, data: dict, **filter_by):
        async with self.async_session() as session:
            stmt = update(ProcessedMessage).filter_by(**filter_by).values(**data)
            await session.execute(stmt)
            await session.commit()

    async def get_one_parser_data(self, **filter_by) -> ParserData | None:
        async with self.async_session() as session:
            query = select(ParserData).filter_by(**filter_by)
            result = await session.execute(query)

            return result.scalar_one_or_none()

    async def get_all_parser_data(self) -> Sequence[ParserData]:
        async with self.async_session() as session:
            query = select(ParserData)
            result = await session.execute(query)

            return result.scalars().all()

    async def update_parser_data(self, data: dict, **filter_by) -> ParserData | None:
        async with self.async_session() as session:
            stmt = (
                update(ParserData)
                .filter_by(**filter_by)
                .values(**data)
                .returning(ParserData)
            )
            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one_or_none()

    async def add_include_keywords_for_parser_data(
        self, new_include_keywords: list[str], parser_data_id: int
    ):
        async with self.async_session() as session:
            stmt = (
                update(ParserData)
                .where(ParserData.id == parser_data_id)
                .values(
                    keywords=func.array_cat(ParserData.keywords, new_include_keywords)
                )
                .returning(ParserData)
            )
            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one_or_none()

    async def delete_include_keywords_for_parser_data(
        self, keywords_to_remove: list[str], parser_data_id: int
    ) -> ParserData | None:
        async with self.async_session() as session:
            result = await session.execute(
                select(ParserData).where(ParserData.id == parser_data_id)
            )
            parser_data = result.scalar_one_or_none()

            if not parser_data:
                return None

            new_keywords = [
                kw for kw in parser_data.keywords if kw not in keywords_to_remove
            ]

            stmt = (
                update(ParserData)
                .where(ParserData.id == parser_data_id)
                .values(keywords=new_keywords)
                .returning(ParserData)
            )
            result = await session.execute(stmt)
            updated_data = result.scalar_one_or_none()
            await session.commit()

            return updated_data

    async def get_exclude_parser_data(self) -> ExcludeParserData | None:
        async with self.async_session() as session:
            query = select(ExcludeParserData)
            result = await session.execute(query)

            return result.scalar_one_or_none()

    async def add_exclude_keywords(
        self, new_exclude_keywords: list[str], exclude_keywords_id: int = 1
    ):
        async with self.async_session() as session:
            stmt = (
                update(ExcludeParserData)
                .where(ExcludeParserData.id == exclude_keywords_id)
                .values(
                    keywords=func.array_cat(
                        ExcludeParserData.keywords, new_exclude_keywords
                    )
                )
                .returning(ExcludeParserData)
            )
            result = await session.execute(stmt)
            await session.commit()

            return result.scalar_one_or_none()

    async def delete_exclude_keywords(
        self, keywords_to_remove: list[str], exclude_keywords_id: int = 1
    ) -> ExcludeParserData | None:
        async with self.async_session() as session:
            result = await session.execute(
                select(ExcludeParserData).where(
                    ExcludeParserData.id == exclude_keywords_id
                )
            )
            exclude_data = result.scalar_one_or_none()

            if not exclude_data:
                return None

            new_keywords = [
                kw for kw in exclude_data.keywords if kw not in keywords_to_remove
            ]

            stmt = (
                update(ExcludeParserData)
                .where(ExcludeParserData.id == exclude_keywords_id)
                .values(keywords=new_keywords)
                .returning(ExcludeParserData)
            )
            result = await session.execute(stmt)
            updated_data = result.scalar_one_or_none()
            await session.commit()

            return updated_data
