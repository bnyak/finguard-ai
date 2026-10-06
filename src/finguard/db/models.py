from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from finguard.db.database import Base

class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "finguard"}

    id: Mapped[int] = mapped_column( BigInteger, primary_key=True, autoincrement=True, )
    filename: Mapped[str] = mapped_column(Text, nullable=False, )
    source_path: Mapped[str | None] = mapped_column(Text, nullable=True, )
    created_at: Mapped[datetime] = mapped_column( DateTime(timezone=True),
        server_default=func.now(), nullable=False, )
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",cascade="all, delete-orphan", )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "page_number",
            "chunk_index",
            name="uq_document_chunk_position",
        ),
        {"schema": "finguard"},
    )

    id: Mapped[int] = mapped_column(BigInteger,
        primary_key=True, autoincrement=True, )
    document_id: Mapped[int] = mapped_column(
        ForeignKey( "finguard.documents.id", ondelete="CASCADE", ),
        nullable=False, )
    page_number: Mapped[int] = mapped_column( Integer, nullable=False, )
    chunk_index: Mapped[int] = mapped_column( Integer, nullable=False, )
    text: Mapped[str] = mapped_column(Text, nullable=False, )
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(384), nullable=True, )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, )

    document: Mapped["Document"] = relationship( back_populates="chunks", )