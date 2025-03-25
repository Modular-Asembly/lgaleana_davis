from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers.dashboard_data import get_dashboard_data

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    """
    Renders the HTML dashboard view by calling the 
    'get dashboard data' endpoint to fetch aggregated dashboard data.
    """
    # Call the get_dashboard_data function to retrieve dashboard metrics and data.
    # The function signature returns a dictionary with keys: metrics, shopify_data, google_ads_data.
    data = get_dashboard_data(db)
    
    # Combine data with the request for rendering the Jinja2 template.
    context = {"request": request}
    context.update(data)
    return templates.TemplateResponse("dashboard.html", context)
