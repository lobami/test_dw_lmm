from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from . import crud as crud_module, schemas as schemas, models as models
from ..database import get_db
from ..security import get_current_user, role_required
from ..users import models as users_models

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/", response_model=Dict[str, Any])
def read_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=100),
    tipo_campania: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(get_current_user)
):
    """
    Get all campaigns with pagination and optional filtering by campaign type.
    """
    # Return only campaigns that belong to the user's company
    if current_user.company_id is None:
        return {"data": [], "total": 0, "page": 0, "pageSize": limit}
    campaigns = crud_module.get_campaigns_for_company(
        db,
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        tipo_campania=tipo_campania,
        start_date=start_date,
        end_date=end_date,
    )
    total = crud_module.get_campaigns_count_for_company(
        db,
        company_id=current_user.company_id,
        tipo_campania=tipo_campania,
        start_date=start_date,
        end_date=end_date,
    )
    campaigns_json = jsonable_encoder(campaigns)
    return {
        "data": campaigns_json,
        "total": total,
        "page": skip // limit,
        "pageSize": limit
    }


@router.get("/{campaign_id}", response_model=schemas.CampaignDetail)
def read_campaign(campaign_id: str, db: Session = Depends(get_db), current_user: users_models.User = Depends(get_current_user)):
    """
    Get detailed information for a specific campaign.
    """
    if current_user.company_id is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign = crud_module.get_campaign_for_company(db, campaign_id, current_user.company_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign



@router.post("/", response_model=schemas.Campaign, status_code=201)
def create_campaign_endpoint(
    campaign_in: schemas.CampaignBase = Body(...),
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(role_required("admin")),
):
    if current_user.company_id is None:
        raise HTTPException(status_code=400, detail="User has no company")
    data = campaign_in.model_dump()
    campaign = crud_module.create_campaign(db, data, current_user.company_id)
    return campaign


@router.put("/{campaign_id}", response_model=schemas.Campaign)
def update_campaign_endpoint(
    campaign_id: str,
    update: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(role_required("admin")),
):
    if current_user.company_id is None:
        raise HTTPException(status_code=400, detail="User has no company")
    campaign = crud_module.update_campaign(db, campaign_id, update, current_user.company_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.delete("/{campaign_id}", status_code=204)
def delete_campaign_endpoint(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(role_required("owner")),
):
    if current_user.company_id is None:
        raise HTTPException(status_code=400, detail="User has no company")
    ok = crud_module.delete_campaign(db, campaign_id, current_user.company_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return None


@router.get("/search-by-date/", response_model=List[schemas.Campaign])
def search_campaigns_by_date(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: users_models.User = Depends(get_current_user)
):
    """
    Search campaigns by date range.
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date"
        )
    
    if current_user.company_id is None:
        return []
    campaigns = crud_module.search_campaigns_by_date_for_company(
        db,
        company_id=current_user.company_id,
        start_date=start_date,
        end_date=end_date
    )
    return campaigns
