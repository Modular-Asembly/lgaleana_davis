from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db import Base

class GoogleAdsData(Base):
    __tablename__ = "google_ads_data"

    id = Column(Integer, primary_key=True, index=True)
    google_ads_id = Column(String, unique=True, nullable=False, index=True)
    campaign_name = Column(String, nullable=False)
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    cost = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
