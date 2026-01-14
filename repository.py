from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from config import DATABASE_URL

from models import (
    Base,
    Announcement,
    SourcePDF,
    OwnershipDisclosure,
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class OwnershipRepository:
    def announcement_exists(self, announcement_id: str) -> bool:
        with session_scope() as session:
            return (
                session.query(Announcement)
                .filter(Announcement.announcement_id == announcement_id)
                .first()
                is not None
            )

    def save_announcement(self, ann, is_backfill: bool = False) -> Announcement:
        with session_scope() as session:
            announcement = Announcement(
                announcement_id=ann.id,
                announcement_no=ann.announcement_no,
                title=ann.title,
                publish_date=ann.publish_date,
                is_backfill=is_backfill,
            )
            session.add(announcement)
            session.flush()
            return announcement

    def save_pdf(
        self,
        announcement_id: int,
        pdf_url: str,
        pdf_hash: str,
        original_filename: str,
        local_path: str,
    ) -> SourcePDF:
        with session_scope() as session:
            pdf = SourcePDF(
                announcement_id=announcement_id,
                pdf_url=pdf_url,
                pdf_hash=pdf_hash,
                original_filename=original_filename,
                local_path=local_path,
            )
            session.add(pdf)
            session.flush()
            return pdf

    def mark_pdf_parsed(self, pdf_id: int, status: str):
        with session_scope() as session:
            session.query(SourcePDF).filter(
                SourcePDF.id == pdf_id
            ).update(
                {
                    SourcePDF.status: status,
                    SourcePDF.parsed_at: None,
                }
            )

    def save_ownership_records(self, pdf_id: int, records: list):
        """
        records = [
          {
            "stock_code": "BBCA",
            "company_name": "Bank Central Asia",
            "shareholder_name": "XYZ Holdings",
            "ownership_percent": 6.23,
            "effective_date": date(...),
            "announcement_date": date(...)
          }
        ]
        """
        with session_scope() as session:
            for r in records:
                obj = OwnershipDisclosure(
                    source_pdf_id=pdf_id,
                    stock_code=r["stock_code"],
                    company_name=r.get("company_name"),
                    shareholder_name=r["shareholder_name"],
                    ownership_percent=r["ownership_percent"],
                    effective_date=r.get("effective_date"),
                    announcement_date=r["announcement_date"],
                )
                session.add(obj)

            try:
                session.flush()
            except IntegrityError:
                # duplicate rows are expected occasionally
                session.rollback()
