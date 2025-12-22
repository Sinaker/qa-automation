from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil

from database import get_db
from models import Order, OrderItem, Cart, CartItem, Product, User
from schemas import (
    CreateOrder,
    UpdateOrderStatus,
    OrderResponse,
    PaginatedOrders,
    Pagination,
    OrderStatusEnum
)
from auth import get_current_user, get_current_admin_user

router = APIRouter()


def calculate_order_totals(items: list) -> dict:
    """Calculate order subtotal, tax, shipping, and total."""
    subtotal = sum(item["quantity"] * item["price"] for item in items)
    tax = subtotal * 0.08  # 8% tax rate
    shipping_cost = 10.0 if subtotal < 100 else 0.0  # Free shipping over $100
    total = subtotal + tax + shipping_cost
    
    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "shippingCost": round(shipping_cost, 2),
        "total": round(total, 2)
    }


@router.get("", response_model=PaginatedOrders)
def list_orders(
    status_filter: Optional[OrderStatusEnum] = Query(None, alias="status", description="Filter by order status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for the authenticated user."""
    query = db.query(Order).filter(Order.userId == current_user.id)
    
    # Apply status filter
    if status_filter:
        query = query.filter(Order.status == status_filter.value)
    
    # Order by creation date (newest first)
    query = query.order_by(Order.createdAt.desc())
    
    # Get total count
    total_items = query.count()
    total_pages = ceil(total_items / limit)
    
    # Apply pagination
    offset = (page - 1) * limit
    orders = query.offset(offset).limit(limit).all()
    
    return {
        "data": orders,
        "pagination": {
            "page": page,
            "limit": limit,
            "totalPages": total_pages,
            "totalItems": total_items
        }
    }


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: CreateOrder,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Place a new order from the cart."""
    # Get user's cart
    cart = db.query(Cart).filter(Cart.userId == current_user.id).first()
    
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Prepare order items and check stock
    order_items_data = []
    for cart_item in cart.items:
        product = cart_item.product
        
        # Check stock availability
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product: {product.name}"
            )
        
        order_items_data.append({
            "productId": product.id,
            "productName": product.name,
            "price": product.price,
            "quantity": cart_item.quantity
        })
    
    # Calculate totals
    totals = calculate_order_totals(order_items_data)
    
    # Create order
    db_order = Order(
        userId=current_user.id,
        shippingAddress=order_data.shippingAddress.model_dump(),
        paymentMethod=order_data.paymentMethod.value,
        status="pending",
        subtotal=totals["subtotal"],
        tax=totals["tax"],
        shippingCost=totals["shippingCost"],
        total=totals["total"],
        notes=order_data.notes
    )
    
    db.add(db_order)
    db.flush()  # Get order ID
    
    # Create order items and update product stock
    for item_data in order_items_data:
        order_item = OrderItem(
            orderId=db_order.id,
            productId=item_data["productId"],
            productName=item_data["productName"],
            price=item_data["price"],
            quantity=item_data["quantity"],
            subtotal=round(item_data["price"] * item_data["quantity"], 2)
        )
        db.add(order_item)
        
        # Update product stock
        product = db.query(Product).filter(Product.id == item_data["productId"]).first()
        product.stock -= item_data["quantity"]
    
    # Clear cart
    db.query(CartItem).filter(CartItem.cartId == cart.id).delete()
    
    db.commit()
    db.refresh(db_order)
    
    return db_order


@router.get("/{orderId}", response_model=OrderResponse)
def get_order_by_id(
    orderId: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve detailed order information."""
    order = db.query(Order).filter(Order.id == orderId).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Users can only view their own orders unless they're admin
    if order.userId != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


@router.patch("/{orderId}", response_model=OrderResponse)
def update_order_status(
    orderId: int,
    status_data: UpdateOrderStatus,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update the status of an order (Admin only)."""
    order = db.query(Order).filter(Order.id == orderId).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validate status transition
    valid_transitions = {
        "pending": ["processing", "cancelled"],
        "processing": ["shipped", "cancelled"],
        "shipped": ["delivered"],
        "delivered": [],
        "cancelled": []
    }
    
    if status_data.status.value not in valid_transitions.get(order.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {order.status} to {status_data.status.value}"
        )
    
    order.status = status_data.status.value
    
    if status_data.trackingNumber:
        order.trackingNumber = status_data.trackingNumber
    
    db.commit()
    db.refresh(order)
    
    return order


@router.delete("/{orderId}", response_model=OrderResponse)
def cancel_order(
    orderId: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an order (only if status is pending)."""
    order = db.query(Order).filter(Order.id == orderId).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Users can only cancel their own orders unless they're admin
    if order.userId != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order"
        )
    
    # Can only cancel pending orders
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel order in current status"
        )
    
    # Restore product stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.productId).first()
        if product:
            product.stock += item.quantity
    
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    
    return order
