from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Float,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    announcement_id = Column(String(255), unique=True, nullable=False)
    announcement_no = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    publish_date = Column(DateTime, nullable=False)
    is_backfill = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    pdfs = relationship("SourcePDF", back_populates="announcement")


class SourcePDF(Base):
    __tablename__ = "source_pdfs"

    id = Column(Integer, primary_key=True)
    announcement_id = Column(
        Integer, ForeignKey("announcements.id"), nullable=False
    )

    pdf_url = Column(String(500), nullable=False)
    pdf_hash = Column(String(64), nullable=False)
    original_filename = Column(String(255), nullable=True)
    local_path = Column(String(500), nullable=False)

    parsed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING / SUCCESS / FAILED

    created_at = Column(DateTime, default=datetime.utcnow)

    announcement = relationship("Announcement", back_populates="pdfs")

    __table_args__ = (
        UniqueConstraint("pdf_hash", name="uq_pdf_hash"),
    )


class OwnershipDisclosure(Base):
    __tablename__ = "ownership_disclosures"

    id = Column(Integer, primary_key=True)

    source_pdf_id = Column(
        Integer, ForeignKey("source_pdfs.id"), nullable=False
    )

    stock_code = Column(String(20), nullable=False)
    company_name = Column(String(255), nullable=True)
    shareholder_name = Column(String(255), nullable=False)

    ownership_percent = Column(Float, nullable=False)
    effective_date = Column(Date, nullable=True)
    announcement_date = Column(Date, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "stock_code",
            "shareholder_name",
            "announcement_date",
            name="uq_ownership_dedup",
        ),
    )
