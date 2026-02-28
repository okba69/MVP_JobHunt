from sqlalchemy import Column, Integer, String, DateTime
from backend.database import Base
import datetime

class JobOffer(Base):
    __tablename__ = "job_offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    url = Column(String, unique=True, index=True)
    contract_type = Column(String)
    published_date = Column(String)
    status = Column(String, default="NEW") # NEW, SELECTED, APPLIED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
