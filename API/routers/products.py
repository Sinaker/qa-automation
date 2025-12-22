from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil

from database import get_db
from models import Product, User
from schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    PaginatedProducts,
    Pagination,
    CategoryEnum,
    SortByEnum,
    SortOrderEnum
)
from auth import get_current_user, get_current_admin_user

router = APIRouter()


@router.get("", response_model=PaginatedProducts)
def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[CategoryEnum] = Query(None, description="Filter by category"),
    minPrice: Optional[float] = Query(None, ge=0, description="Minimum price"),
    maxPrice: Optional[float] = Query(None, ge=0, description="Maximum price"),
    inStock: Optional[bool] = Query(None, description="Filter by stock availability"),
    sortBy: Optional[SortByEnum] = Query(None, description="Sort field"),
    sortOrder: SortOrderEnum = Query(SortOrderEnum.asc, description="Sort order"),
    db: Session = Depends(get_db)
):
    """Get a paginated list of products with optional filters."""
    query = db.query(Product)
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category.value)
    
    if minPrice is not None:
        query = query.filter(Product.price >= minPrice)
    
    if maxPrice is not None:
        query = query.filter(Product.price <= maxPrice)
    
    if inStock is not None:
        if inStock:
            query = query.filter(Product.stock > 0)
        else:
            query = query.filter(Product.stock == 0)
    
    # Apply sorting
    if sortBy:
        sort_column = getattr(Product, sortBy.value)
        if sortOrder == SortOrderEnum.desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    
    # Get total count
    total_items = query.count()
    total_pages = ceil(total_items / limit)
    
    # Apply pagination
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    return {
        "data": products,
        "pagination": {
            "page": page,
            "limit": limit,
            "totalPages": total_pages,
            "totalItems": total_items
        }
    }


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Add a new product to the catalog (Admin only)."""
    db_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category.value,
        stock=product_data.stock,
        images=product_data.images,
        tags=product_data.tags
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.get("/{productId}", response_model=ProductResponse)
def get_product_by_id(productId: int, db: Session = Depends(get_db)):
    """Retrieve detailed product information."""
    product = db.query(Product).filter(Product.id == productId).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.put("/{productId}", response_model=ProductResponse)
def update_product(
    productId: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update product information (Admin only)."""
    product = db.query(Product).filter(Product.id == productId).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update product fields
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.stock is not None:
        product.stock = product_data.stock
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{productId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    productId: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Remove a product from the catalog (Admin only)."""
    product = db.query(Product).filter(Product.id == productId).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    
    return None
