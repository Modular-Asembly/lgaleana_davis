import os
from datetime import datetime
from typing import Any, Dict, List

import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.shopify_data import ShopifyData

router = APIRouter(prefix="/shopify", tags=["Shopify"])

def fetch_shopify_data() -> List[Dict[str, Any]]:
    """
    Authenticates with Shopify using API credentials from environment variables,
    retrieves product data and returns a list of dictionaries with the required fields.

    Returns:
        A list of dictionaries each representing a Shopify product.
    """
    shopify_api_key: str = os.environ["SHOPIFY_API_KEY"]
    shopify_api_password: str = os.environ["SHOPIFY_API_PASSWORD"]
    shopify_shop_name: str = os.environ["SHOPIFY_SHOP_NAME"]

    # Build the Shopify URL endpoint for products
    url: str = f"https://{shopify_shop_name}.myshopify.com/admin/api/2023-10/products.json"

    # Make the HTTPS GET request with basic auth
    response = requests.get(url, auth=(shopify_api_key, shopify_api_password))
    response.raise_for_status()

    products = response.json().get("products", [])
    results: List[Dict[str, Any]] = []
    for product in products:
        # Use product id as shopify_id, title from product title, price from first variant if exists.
        shopify_id: str = str(product.get("id"))
        title: str = product.get("title", "")
        price: float = 0.0
        variants = product.get("variants", [])
        if variants:
            # Assume first variant price can be used; convert string to float.
            price_str = variants[0].get("price", "0.0")
            try:
                price = float(price_str)
            except ValueError:
                price = 0.0

        entry: Dict[str, Any] = {
            "shopify_id": shopify_id,
            "title": title,
            "price": price,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        results.append(entry)
    return results

def persist_shopify_data(db: Session, data: List[Dict[str, Any]]) -> None:
    """
    Inserts the list of product data dictionaries into the database.
    For each entry, check for an existing record by shopify_id to avoid duplicates.

    Args:
        db: The database session.
        data: A list of dictionaries each representing product data to persist.
    """
    for record in data:
        existing = db.query(ShopifyData).filter(
            ShopifyData.shopify_id == record["shopify_id"]
        ).first()
        if not existing:
            new_entry = ShopifyData(
                shopify_id=record["shopify_id"],
                title=record["title"],
                price=record["price"],
                created_at=record["created_at"],
                updated_at=record["updated_at"],
            )
            db.add(new_entry)
    db.commit()

@router.post("/pull", response_model=Dict[str, Any])
def pull_shopify_data(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Pulls product data from Shopify and persists it into the database.
    Returns a JSON payload with summary details.

    Args:
        db: Database session injected via dependency.

    Returns:
        A dictionary with the status and number of inserted records.
    """
    products_data: List[Dict[str, Any]] = fetch_shopify_data()
    persist_shopify_data(db, products_data)
    return {
        "status": "success",
        "inserted_records": len(products_data)
    }
