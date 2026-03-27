from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Category, User, ProductionEntry, MenuItem
from auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: int
    name: str
    created_by: int

class MenuItemResponse(BaseModel):
    id: int
    name: str
    type: str
    is_active: bool
    category_id: int
    category_name: str

@router.post("/categories", response_model=CategoryResponse, status_code=201)
def add_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if name exists
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    db_category = Category(
        name=category.name,
        created_by=current_user.id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.put("/categories/{category_id}", response_model=CategoryResponse)
def edit_category(
    category_id: int,
    category: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check unique name
    existing = db.query(Category).filter(Category.name == category.name, Category.id != category_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if used
    if db.query(ProductionEntry).filter(ProductionEntry.category_id == category_id).first() or db.query(MenuItem).filter(MenuItem.category_id == category_id).first():
        raise HTTPException(status_code=400, detail="Category has entries/items, delete them first")
    
    db.delete(db_category)
    db.commit()
    return None

@router.get("/menu-items", response_model=List[MenuItemResponse])
def list_menu_items(db: Session = Depends(get_db)):
    items = db.query(MenuItem).join(Category).all()
    return [{"id": item.id, "name": item.name, "type": item.type, "is_active": item.is_active, "category_id": item.category_id, "category_name": item.category.name} for item in items]

