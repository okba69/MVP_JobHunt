import pytest
from sqlalchemy import inspect
from backend.database import engine, Base
from backend.models import JobOffer

def test_database_tables_created():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    assert "job_offers" in inspector.get_table_names()
