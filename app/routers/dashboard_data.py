from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.shopify_data import ShopifyData
from app.models.google_ads_data import GoogleAdsData

router = APIRouter(prefix="/dashboard-data", tags=["Dashboard Data"])

def serialize_shopify_data(item: ShopifyData) -> Dict[str, Any]:
    return {
        "id": item.id,
        "shopify_id": item.shopify_id,
        "title": item.title,
        "price": item.price,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat()
    }

def serialize_google_ads_data(item: GoogleAdsData) -> Dict[str, Any]:
    return {
        "id": item.id,
        "google_ads_id": item.google_ads_id,
        "campaign_name": item.campaign_name,
        "impressions": item.impressions,
        "clicks": item.clicks,
        "cost": item.cost,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat()
    }

@router.get("/", response_model=Dict[str, Any])
def get_dashboard_data(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Aggregates data from ShopifyData and GoogleAdsData tables.
    Returns a JSON payload that includes key metrics and data for the dashboard.
    """
    # Retrieve all Shopify data records.
    shopify_records: List[ShopifyData] = db.query(ShopifyData).all()
    shopify_data: List[Dict[str, Any]] = [serialize_shopify_data(item) for item in shopify_records]

    # Retrieve all Google Ads data records.
    google_ads_records: List[GoogleAdsData] = db.query(GoogleAdsData).all()
    google_ads_data: List[Dict[str, Any]] = [serialize_google_ads_data(item) for item in google_ads_records]

    # Compute key metrics: counts for demonstration.
    dashboard_metrics: Dict[str, Any] = {
        "shopify_total": len(shopify_data),
        "google_ads_total": len(google_ads_data)
    }

    return {
        "metrics": dashboard_metrics,
        "shopify_data": shopify_data,
        "google_ads_data": google_ads_data
    }
