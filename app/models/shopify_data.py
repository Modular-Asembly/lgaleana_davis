from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db import Base

class ShopifyData(Base):
    __tablename__ = "shopify_data"

    id = Column(Integer, primary_key=True, index=True)
    shopify_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
