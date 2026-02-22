import time
from typing import Optional
from fastapi import APIRouter, Form, Response, UploadFile, status, HTTPException, Depends
from fastapi.params import File
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..schemas import MarketResponse, CreateMarket, UpdateMarket
from ..oauth2 import get_current_user
#from ..oauth2 import get_current_user
#from ..main_alchemy import limiter
from fastapi import BackgroundTasks
import asyncio

router = APIRouter(
    tags=["Markets"]
)



 
@router.get("/markets", status_code=status.HTTP_200_OK,response_model=list[MarketResponse])
def get_markets(db: Session = Depends(get_db), limit: int = 20, skip: int = 0, starts_by: Optional[str] = "", order_by: Optional[str] = "id"):

    try:
        markets = db.query(models.Market).filter(
            models.Market.name.like(f"{starts_by}%"),
        ).order_by(getattr(models.Market, order_by)).offset(skip).limit(limit).all()
        
        #print(f"Verbs: {verbs}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error fetching Leagues: {e} \n Check your query parameters"
        )
    if not markets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Markets found"
        )
    
    return markets


@router.get("/market/{market_id}", status_code=status.HTTP_200_OK, response_model=MarketResponse)
def get_market(market_id: int, db: Session = Depends(get_db)):
    market = db.query(models.Market).filter(models.Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market




@router.post("/market", status_code=status.HTTP_201_CREATED)
async def create_market(market: CreateMarket, db: Session = Depends(get_db)
):

    last_id = db.query(models.Market.id).order_by(models.Market.id.desc()).first()
    new_id = (last_id[0] if last_id else 0) + 1
    new_market = models.Market(id=new_id,name=market.name, created_at=time.strftime("%Y-%m-%d %H:%M:%S"), updated_at=time.strftime("%Y-%m-%d %H:%M:%S"))



    try:
        db.add(new_market)
        db.commit()
        db.refresh(new_market)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating Market: {e}")
    return {"id": new_market.id, "name": new_market.name}


@router.put("/market/{market_id}", status_code=status.HTTP_200_OK)
def update_market(market_id: int, market: UpdateMarket, db: Session = Depends(get_db)):
    market_to_update = db.query(models.Market).filter(models.Market.id == market_id).first()
    if not market_to_update:
        raise HTTPException(status_code=404, detail="Market not found")
    
    market_to_update.name = market.name
    market_to_update.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        db.commit()
        db.refresh(market_to_update)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating Market: {e}")
    
    return {"id": market_to_update.id, "name": market_to_update.name}


@router.delete("/market/{market_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_market(market_id: int, db: Session = Depends(get_db)):
    market_to_delete = db.query(models.Market).filter(models.Market.id == market_id).first()
    if not market_to_delete:
        raise HTTPException(status_code=404, detail="Market not found")
    
    try:
        db.delete(market_to_delete)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting Market: {e}")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)