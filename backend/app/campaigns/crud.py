from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Optional
from ..campaigns import models
import logging


def get_campaigns(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    tipo_campania: Optional[str] = None
):
    logger = logging.getLogger("app.campaigns.crud")
    logger.debug("get_campaigns", extra={"skip": skip, "limit": limit, "tipo_campania": tipo_campania})
    query = db.query(models.Campaign)
    if tipo_campania:
        query = query.filter(models.Campaign.tipo_campania == tipo_campania)
    return query.offset(skip).limit(limit).all()


def get_campaigns_for_company(
    db: Session,
    company_id: int,
    skip: int = 0,
    limit: int = 10,
    tipo_campania: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    logger = logging.getLogger("app.campaigns.crud")
    logger.debug("get_campaigns_for_company", extra={"company_id": company_id, "skip": skip, "limit": limit, "tipo_campania": tipo_campania})
    query = db.query(models.Campaign).filter(models.Campaign.company_id == company_id)
    if tipo_campania:
        query = query.filter(models.Campaign.tipo_campania == tipo_campania)
    if start_date and end_date:
        query = query.filter(
            and_(
                models.Campaign.fecha_inicio <= end_date,
                models.Campaign.fecha_fin >= start_date
            )
        )
    return query.offset(skip).limit(limit).all()


def create_campaign(db: Session, campaign_in: dict, company_id: int):
    logger = logging.getLogger("app.campaigns.crud")
    logger.info("create_campaign", extra={"company_id": company_id, "data": campaign_in})
    campaign = models.Campaign(**campaign_in)
    campaign.company_id = company_id
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    # Campaign primary key is 'name'
    logger.debug("create_campaign_done", extra={"campaign_name": campaign.name})
    return campaign


def update_campaign(db: Session, campaign_id: str, update_data: dict, company_id: int):
    campaign = get_campaign_for_company(db, campaign_id, company_id)
    if not campaign:
        return None
    for k, v in update_data.items():
        if hasattr(campaign, k):
            setattr(campaign, k, v)
    db.commit()
    db.refresh(campaign)
    logging.getLogger("app.campaigns.crud").info("update_campaign", extra={"campaign_id": campaign_id, "company_id": company_id, "changes": update_data})
    return campaign


def delete_campaign(db: Session, campaign_id: str, company_id: int):
    campaign = get_campaign_for_company(db, campaign_id, company_id)
    if not campaign:
        return False
    logging.getLogger("app.campaigns.crud").info("delete_campaign", extra={"campaign_id": campaign_id, "company_id": company_id})
    db.delete(campaign)
    db.commit()
    return True

def get_campaign(db: Session, campaign_id: str):
    return db.query(models.Campaign).filter(models.Campaign.name == campaign_id).first()


def get_campaign_for_company(db: Session, campaign_id: str, company_id: int):
    return db.query(models.Campaign).filter(
        models.Campaign.name == campaign_id,
        models.Campaign.company_id == company_id
    ).first()

def search_campaigns_by_date(
    db: Session,
    start_date: datetime,
    end_date: datetime
):
    return db.query(models.Campaign).filter(
        and_(
            models.Campaign.fecha_inicio <= end_date,
            models.Campaign.fecha_fin >= start_date
        )
    ).all()


def search_campaigns_by_date_for_company(
    db: Session,
    company_id: int,
    start_date: datetime,
    end_date: datetime
):
    return db.query(models.Campaign).filter(
        models.Campaign.company_id == company_id,
        and_(
            models.Campaign.fecha_inicio <= end_date,
            models.Campaign.fecha_fin >= start_date
        )
    ).all()


def get_campaigns_count_for_company(
    db: Session,
    company_id: int,
    tipo_campania: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(models.Campaign).filter(models.Campaign.company_id == company_id)
    if tipo_campania:
        query = query.filter(models.Campaign.tipo_campania == tipo_campania)
    if start_date and end_date:
        query = query.filter(
            and_(
                models.Campaign.fecha_inicio <= end_date,
                models.Campaign.fecha_fin >= start_date
            )
        )
    return query.count()
