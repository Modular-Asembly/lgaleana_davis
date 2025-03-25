import os
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import requests

from app.db import get_db
from app.models.google_ads_data import GoogleAdsData

router = APIRouter(prefix="/google-ads", tags=["Google Ads"])

def fetch_google_ads_data() -> List[Dict[str, Any]]:
    """
    Authenticates with Google Ads using OAuth credentials from environment variables,
    retrieves advertising data and returns a list of dictionaries with the required fields.
    """
    # Retrieve credentials from environment variables.
    developer_token: str = os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"]
    client_id: str = os.environ["GOOGLE_ADS_CLIENT_ID"]
    client_secret: str = os.environ["GOOGLE_ADS_CLIENT_SECRET"]
    refresh_token: str = os.environ["GOOGLE_ADS_REFRESH_TOKEN"]
    # Optionally, if provided.
    login_customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")

    # Build configuration dict for GoogleAdsClient.
    client_config: Dict[str, Any] = {
        "developer_token": developer_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }
    if login_customer_id:
        client_config["login_customer_id"] = login_customer_id

    # Initialize the Google Ads client.
    google_ads_client: GoogleAdsClient = GoogleAdsClient.load_from_dict(client_config)
    ga_service = google_ads_client.get_service("GoogleAdsService")

    # Define a GAQL query to retrieve campaign metrics.
    query: str = ("""
        SELECT
          campaign.id,
          campaign.name,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros
        FROM campaign
        WHERE segments.date DURING TODAY
    """)

    # Replace with your Google Ads customer ID.
    customer_id: str = os.environ["GOOGLE_ADS_CLIENT_ID"]

    # Execute the query.
    response = ga_service.search(customer_id=customer_id, query=query)
    
    # Process the result set.
    results: List[Dict[str, Any]] = []
    for row in response:
        # Convert cost from micros to standard currency unit.
        cost: float = row.metrics.cost_micros / 1_000_000.0
        entry: Dict[str, Any] = {
            "google_ads_id": str(row.campaign.id),
            "campaign_name": row.campaign.name,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "cost": cost,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        results.append(entry)
    return results

def persist_google_ads_data(db: Session, data: List[Dict[str, Any]]) -> None:
    """
    Inserts the list of advertising data dictionaries into the database.
    """
    for record in data:
        # Check for existing record by google_ads_id to avoid duplicates.
        existing = db.query(GoogleAdsData).filter(
            GoogleAdsData.google_ads_id == record["google_ads_id"]
        ).first()
        if not existing:
            new_entry = GoogleAdsData(
                google_ads_id=record["google_ads_id"],
                campaign_name=record["campaign_name"],
                impressions=record["impressions"],
                clicks=record["clicks"],
                cost=record["cost"],
                created_at=record["created_at"],
                updated_at=record["updated_at"],
            )
            db.add(new_entry)
    db.commit()

@router.post("/pull", response_model=Dict[str, Any])
def pull_google_ads_data(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Pulls data from Google Ads and persists it into the database.
    Returns a JSON payload with summary data.
    """
    # Fetch advertising data from Google Ads.
    ads_data: List[Dict[str, Any]] = fetch_google_ads_data()

    # Persist the fetched data into the database.
    persist_google_ads_data(db, ads_data)

    return {
        "status": "success",
        "inserted_records": len(ads_data)
    }
