from datetime import datetime
from sqlalchemy import (
    Text,
    Integer,
    String,
    DateTime,
    BigInteger,
    Boolean,
    func,
    ARRAY,
    Enum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from database.enums import ProcessedMessageStatus


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sender_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    matched_keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    message_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class ProcessedMessage(Base):
    __tablename__ = "processed_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipient_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ProcessedMessageStatus] = mapped_column(
        Enum(ProcessedMessageStatus, name="message_status", native_enum=False),
        default=ProcessedMessageStatus.waiting,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_replied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    replied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class ParserData(Base):
    __tablename__ = "parser_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)


class ExcludeParserData(Base):
    __tablename__ = "exclude_parser_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keywords: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
