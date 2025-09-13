"""SQLAlchemy models for SR&ED Copilot Lite."""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    project_id = Column(String, index=True)
    path = Column(String, unique=True, nullable=False)
    text = Column(Text, nullable=False)

    chunks = relationship("Chunk", back_populates="document")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    start = Column(Integer)
    end = Column(Integer)
    text = Column(Text)

    document = relationship("Document", back_populates="chunks")
    tags = relationship("Tag", back_populates="chunk")
    citations = relationship("Citation", back_populates="chunk")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, ForeignKey("chunks.id"))
    facet = Column(String, index=True)

    chunk = relationship("Chunk", back_populates="tags")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, ForeignKey("chunks.id"))
    source_path = Column(String)
    char_start = Column(Integer)
    char_end = Column(Integer)

    chunk = relationship("Chunk", back_populates="citations")
