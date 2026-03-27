from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import ProductionEntry, Category, MenuItem, User
from typing import Union, List
from pydantic import Field, validator
from auth import get_current_user

class MenuItemResponse(BaseModel):
    id: int
    name: str
    type: str
    is_active: bool
    category_id: int
    category_name: str

router = APIRouter(prefix="/production-entries", tags=["production"])

class ProductionEntryCreate(BaseModel):
    menu_item_id: int
    quantity: Union[int, float]
    category_id: Optional[int] = None
    unit: str = Field(..., description="kg, portion, pieces")

    @validator('unit')
    def valid_unit(cls, v):
        if v not in ["kg", "portion", "pieces"]:
            raise ValueError('unit must be "kg", "portion" or "pieces"')
        return v

class ProductionEntryResponse(BaseModel):
    id: int
    menu_item_name: str
    category_name: str
    quantity: Union[int, float]
    unit: str
    timestamp: str
    created_by: int

@router.post("/", response_model=ProductionEntryResponse, status_code=201)
def create_production_entry(
    entry: ProductionEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate menu_item exists
    menu_item = db.query(MenuItem).filter(MenuItem.id == entry.menu_item_id, MenuItem.is_active == True).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found or inactive")
    
    category = menu_item.category
    
    # Permissions
    if current_user.role != "admin":
        if current_user.category_id is None:
            raise HTTPException(status_code=403, detail="Cook must be assigned to a category")
        if entry.category_id and entry.category_id != current_user.category_id:
            raise HTTPException(status_code=400, detail="Wrong category for cook")
        if menu_item.category_id != current_user.category_id:
            raise HTTPException(status_code=403, detail="Unauthorized category")
    elif entry.category_id and entry.category_id != menu_item.category_id:
        raise HTTPException(status_code=400, detail="Category does not match menu item")

    db_entry = ProductionEntry(
        menu_item_id=entry.menu_item_id,
        category_id=menu_item.category_id,
        quantity=entry.quantity,
        unit=entry.unit,
        created_by=current_user.id
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return ProductionEntryResponse(
        id=db_entry.id,
        menu_item_name=menu_item.name,
        category_name=category.name,
        quantity=db_entry.quantity,
        unit=db_entry.unit,
        timestamp=db_entry.timestamp.isoformat(),
        created_by=db_entry.created_by
    )

@router.get("/", response_model=List[ProductionEntryResponse])
def get_production_entries(
    category_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ProductionEntry).join(MenuItem).join(Category)
    
    if current_user.role == "cook":
        if current_user.category_id is None:
            raise HTTPException(status_code=403, detail="Cook must be assigned to a category")
        query = query.filter(Category.id == current_user.category_id)
    elif current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    elif category_id:
        query = query.filter(Category.id == category_id)
    
    entries = query.all()
    
    result = []
    for entry in entries:
        result.append(ProductionEntryResponse(
            id=entry.id,
            menu_item_name=entry.menu_item.name,
            category_name=entry.menu_item.category.name,
            quantity=entry.quantity,
            unit=entry.unit,
            timestamp=entry.timestamp.isoformat(),
            created_by=entry.created_by
        ))
    return result

@router.get("/menu-items/", response_model=List[MenuItemResponse])
def get_menu_items(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "cook":
        if current_user.category_id is None:
            raise HTTPException(status_code=403, detail="Cook must be assigned to a category")
        if category_id != current_user.category_id:
            raise HTTPException(status_code=403, detail="Unauthorized category")
    
    items = db.query(MenuItem).filter(
        MenuItem.category_id == category_id,
        MenuItem.is_active == True
    ).join(Category).all()
    
    return [
        MenuItemResponse(
            id=item.id,
            name=item.name,
            type=item.type,
            is_active=item.is_active,
            category_id=item.category_id,
            category_name=item.category.name
        ) for item in items
    ]

