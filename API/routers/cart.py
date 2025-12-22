from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Cart, CartItem, Product, User
from schemas import AddToCart, UpdateCartItem, CartResponse, CartItemResponse
from auth import get_current_user

router = APIRouter()


def calculate_cart_totals(cart: Cart) -> dict:
    """Calculate cart subtotal, tax, and total."""
    subtotal = sum(item.quantity * item.product.price for item in cart.items)
    tax = subtotal * 0.08  # 8% tax rate
    total = subtotal + tax
    
    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "total": round(total, 2)
    }


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    """Get existing cart or create new one for user."""
    cart = db.query(Cart).filter(Cart.userId == user_id).first()
    
    if not cart:
        cart = Cart(userId=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    return cart


@router.get("", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the current user's shopping cart."""
    cart = get_or_create_cart(db, current_user.id)
    
    # Calculate totals
    totals = calculate_cart_totals(cart)
    
    # Build response with cart items
    cart_items = []
    for item in cart.items:
        cart_items.append({
            "id": item.id,
            "productId": item.productId,
            "productName": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "subtotal": round(item.quantity * item.product.price, 2)
        })
    
    return {
        "id": cart.id,
        "userId": cart.userId,
        "items": cart_items,
        "subtotal": totals["subtotal"],
        "tax": totals["tax"],
        "total": totals["total"],
        "updatedAt": cart.updatedAt
    }


@router.post("", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_data: AddToCart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a product to the shopping cart."""
    # Check if product exists
    product = db.query(Product).filter(Product.id == item_data.productId).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if enough stock
    if product.stock < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )
    
    # Get or create cart
    cart = get_or_create_cart(db, current_user.id)
    
    # Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cartId == cart.id,
        CartItem.productId == item_data.productId
    ).first()
    
    if existing_item:
        # Update quantity
        new_quantity = existing_item.quantity + item_data.quantity
        if product.stock < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )
        existing_item.quantity = new_quantity
    else:
        # Add new item
        cart_item = CartItem(
            cartId=cart.id,
            productId=item_data.productId,
            quantity=item_data.quantity
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart)
    
    # Return updated cart
    return get_cart(current_user, db)


@router.put("/items/{itemId}", response_model=CartResponse)
def update_cart_item(
    itemId: int,
    item_data: UpdateCartItem,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the quantity of an item in the cart."""
    cart = get_or_create_cart(db, current_user.id)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == itemId,
        CartItem.cartId == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Check stock availability
    product = cart_item.product
    if product.stock < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )
    
    cart_item.quantity = item_data.quantity
    db.commit()
    db.refresh(cart)
    
    # Return updated cart
    return get_cart(current_user, db)


@router.delete("/items/{itemId}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    itemId: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a specific item from the cart."""
    cart = get_or_create_cart(db, current_user.id)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == itemId,
        CartItem.cartId == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    db.delete(cart_item)
    db.commit()
    
    return None


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove all items from the cart."""
    cart = get_or_create_cart(db, current_user.id)
    
    # Delete all cart items
    db.query(CartItem).filter(CartItem.cartId == cart.id).delete()
    db.commit()
    
    return None
