from sqlalchemy.orm import Session
from database.models import ParserData, ExcludeParserData
from config.settings import settings
from services.logger import Logger

logger = Logger(__name__).setup_logger()


def init_seed_data(bind):
    session = Session(bind=bind)

    try:
        if (
            session.query(ParserData).count() > 0
            or session.query(ExcludeParserData).count() > 0
        ):
            logger.info(
                "🗓 Начальные данные уже загружены... Пропускаем начальный скрипт"
            )
            return

        parser_data = [ParserData(**data) for data in settings.PARSER_DATA]
        session.bulk_save_objects(parser_data)

        exclude_parser_data = [
            ExcludeParserData(**data) for data in settings.EXCLUDE_KEYWORDS
        ]
        session.bulk_save_objects(exclude_parser_data)

        session.commit()
        logger.info("✅ Начальные данные успешно загружены")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Ошибка загрузки начальных данных: {e}")
        raise

    finally:
        session.close()


def clear_seed_data(bind):
    session = Session(bind=bind)

    try:
        session.query(ParserData).delete()
        session.query(ExcludeParserData).delete()
        session.commit()
        logger.info("✅ Начальные данные очищены")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Ошибка очистки начальных данных: {e}")
        raise

    finally:
        session.close()
