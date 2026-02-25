import time
from typing import Optional
from fastapi import APIRouter, Form, Response, UploadFile, status, HTTPException, Depends
from fastapi.params import File
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..schemas import ProductResponse, ProductCreate, ProductUpdate
from ..oauth2 import get_current_user
#from ..oauth2 import get_current_user
#from ..main_alchemy import limiter
from fastapi import BackgroundTasks
import asyncio

router = APIRouter(
    tags=["Products"]
)



 
@router.get("/products", status_code=status.HTTP_200_OK,response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db),limit: int = 20, skip: int = 0, starts_by: Optional[str] = "",l_country: Optional[str] = "", order_by: Optional[str] = "price", background_tasks: BackgroundTasks = None):

    try:
        products = db.query(models.Product).filter(
            models.Product.name.like(f"%{starts_by}%"),
        ).order_by(getattr(models.Product, order_by)).offset(skip).limit(limit).all()
        
        #I want to adjust the market name to get from the market relationship, not from the product table
        for product in products:
            product.market_name = product.market.name if product.market else None
        #print(f"Verbs: {verbs}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error fetching Leagues: {e} \n Check your query parameters"
        )
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Markets found"
        )
    
    return products


@router.get("/product/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.market_name = product.market.name if product.market else None
    return product

@router.post("/product", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):

    last_id = db.query(models.Product.id).order_by(models.Product.id.desc()).first()
    #consider camel Case, uppercase and lower case market names
    market = db.query(models.Market).filter(models.Market.name.ilike(product.market)).first()
    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market '{product.market}' not found. Please create the market before adding products."
        )
    new_id = (last_id[0] if last_id else 0) + 1
    new_product = models.Product(id=new_id,name=product.name, created_at=time.strftime("%Y-%m-%d %H:%M:%S"), updated_at=time.strftime("%Y-%m-%d %H:%M:%S"), market=market, price=product.price)



    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error creating Product: {e}"
        )
    
    return new_product



@router.put("/product/{product_id}", status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):

    existing_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    # Update only the fields that are provided in the request
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_product, key, value)
    
    existing_product.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        db.commit()
        db.refresh(existing_product)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error updating Product: {e}"
        )
    
    return existing_product


@router.delete("/product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):

    existing_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    try:
        db.delete(existing_product)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error deleting Product: {e}"
        )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)