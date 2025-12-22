from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class CategoryEnum(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    books = "books"
    home = "home"
    toys = "toys"


class PaymentMethodEnum(str, Enum):
    credit_card = "credit_card"
    debit_card = "debit_card"
    paypal = "paypal"
    cash_on_delivery = "cash_on_delivery"


class OrderStatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class SortByEnum(str, Enum):
    price = "price"
    name = "name"
    createdAt = "createdAt"
    rating = "rating"


class SortOrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"


# Address Schema
class Address(BaseModel):
    street: str = Field(..., example="123 Main St")
    apartment: Optional[str] = Field(None, example="Apt 4B")
    city: str = Field(..., example="New York")
    state: str = Field(..., example="NY")
    zipCode: str = Field(..., pattern=r"^[0-9]{5}(-[0-9]{4})?$", example="10001")
    country: str = Field(..., example="USA")


# User Schemas
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$", example="john_doe")
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., min_length=8, max_length=100, example="SecurePass123!")
    firstName: Optional[str] = Field(None, max_length=50, example="John")
    lastName: Optional[str] = Field(None, max_length=50, example="Doe")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., example="SecurePass123!")


class UserResponse(BaseModel):
    id: int = Field(..., example=123)
    username: str = Field(..., example="john_doe")
    email: str = Field(..., example="john@example.com")
    firstName: Optional[str] = Field(None, example="John")
    lastName: Optional[str] = Field(None, example="Doe")
    phone: Optional[str] = Field(None, example="+1234567890")
    address: Optional[Address] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    firstName: Optional[str] = Field(None, max_length=50)
    lastName: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    address: Optional[Address] = None


class TokenResponse(BaseModel):
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refreshToken: str = Field(..., example="refresh_token_here")
    expiresIn: int = Field(..., example=3600)


# Product Schemas
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200, example="Wireless Headphones")
    description: Optional[str] = Field(None, max_length=2000, example="High-quality wireless headphones with noise cancellation")
    price: float = Field(..., gt=0, example=99.99)
    category: CategoryEnum = Field(..., example="electronics")
    stock: int = Field(..., ge=0, example=50)
    images: Optional[List[str]] = Field(None, max_items=10)
    tags: Optional[List[str]] = Field(None, max_items=20)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)


class ProductResponse(BaseModel):
    id: int = Field(..., example=456)
    name: str = Field(..., example="Wireless Headphones")
    description: Optional[str] = Field(None, example="High-quality wireless headphones")
    price: float = Field(..., example=99.99)
    category: str = Field(..., example="electronics")
    stock: int = Field(..., example=50)
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    rating: Optional[float] = Field(None, ge=0, le=5, example=4.5)
    reviewCount: int = Field(default=0, example=120)
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# Cart Schemas
class AddToCart(BaseModel):
    productId: int = Field(..., ge=1, example=456)
    quantity: int = Field(..., ge=1, le=100, example=2)


class UpdateCartItem(BaseModel):
    quantity: int = Field(..., ge=1, le=100)


class CartItemResponse(BaseModel):
    id: int = Field(..., example=1)
    productId: int = Field(..., example=456)
    productName: str = Field(..., example="Wireless Headphones")
    price: float = Field(..., example=99.99)
    quantity: int = Field(..., example=3)
    subtotal: float = Field(..., example=299.97)

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int = Field(..., example=1)
    userId: int = Field(..., example=123)
    items: List[CartItemResponse] = []
    subtotal: float = Field(..., example=299.97)
    tax: float = Field(..., example=24.00)
    total: float = Field(..., example=323.97)
    updatedAt: datetime

    class Config:
        from_attributes = True


# Order Schemas
class CreateOrder(BaseModel):
    shippingAddress: Address
    paymentMethod: PaymentMethodEnum = Field(..., example="credit_card")
    notes: Optional[str] = Field(None, max_length=500)


class UpdateOrderStatus(BaseModel):
    status: OrderStatusEnum
    trackingNumber: Optional[str] = Field(None, max_length=100)


class OrderItemResponse(BaseModel):
    id: int
    productId: int
    productName: str
    price: float
    quantity: int
    subtotal: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int = Field(..., example=789)
    userId: int = Field(..., example=123)
    items: List[OrderItemResponse] = []
    shippingAddress: Address
    paymentMethod: str = Field(..., example="credit_card")
    status: str = Field(..., example="processing")
    subtotal: float = Field(..., example=299.97)
    tax: float = Field(..., example=24.00)
    shippingCost: float = Field(..., example=10.00)
    total: float = Field(..., example=333.97)
    trackingNumber: Optional[str] = Field(None, example="TRACK123456")
    notes: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# Pagination Schema
class Pagination(BaseModel):
    page: int = Field(..., example=1)
    limit: int = Field(..., example=20)
    totalPages: int = Field(..., example=5)
    totalItems: int = Field(..., example=97)


class PaginatedProducts(BaseModel):
    data: List[ProductResponse]
    pagination: Pagination


class PaginatedOrders(BaseModel):
    data: List[OrderResponse]
    pagination: Pagination


# Error Schema
class ErrorResponse(BaseModel):
    error: str = Field(..., example="Invalid input")
    message: str = Field(..., example="The email field is required")
    code: str = Field(..., example="VALIDATION_ERROR")
    details: Optional[dict] = None
