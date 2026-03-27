from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="cook")  # "admin" or "cook"
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    categories = relationship("Category", back_populates="users", foreign_keys=[category_id])

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    users = relationship("User", back_populates="categories", foreign_keys="User.category_id")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    menu_items = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    type = Column(String)  # "veg" or "non-veg"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    category = relationship("Category", back_populates="menu_items")
    production_entries = relationship("ProductionEntry", back_populates="menu_item")

class ProductionEntry(Base):
    __tablename__ = "production_entries"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))  # Keep for queries/legacy
    quantity = Column(Integer)
    created_by = Column(Integer, ForeignKey("users.id"))
    unit = Column(String, default="portion")  # kg, portion, pieces
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    menu_item = relationship("MenuItem", back_populates="production_entries")

def seed_menu_data(db: Session):
    if db.query(MenuItem).count() > 0:
        return "Menu already seeded. Skipping."

    
    # Menu data grouped by category
    menu_data = {
        "Appetisers": [
            ("Paneer Kanti", "veg"),
            ("Nadur Monje", "veg"),
            ("Kaladi Kulcha", "veg"),
            ("Aloo Churma", "veg"),
            ("Omelette Kanti", "non-veg"),
            ("Kabargah", "non-veg"),
            ("Wazwan Mutton Seekh", "non-veg"),
            ("Wazwan Chicken Seekh", "non-veg"),
            ("Mutton Seekh Kanti", "non-veg"),
            ("Chicken Seekh Kanti", "non-veg"),
            ("Chicken Lahabdar Kebab", "non-veg"),
        ],
        "Vegetarian Entrees": [
            ("Paneer Roganjosh", "veg"),
            ("Paneer Kaliya", "veg"),
            ("Dum Aloo", "veg"),
            ("Kashmiri Rajma", "veg"),
            ("Nadur Yakhni", "veg"),
            ("Tchok Wangun", "veg"),
            ("Monje Haak", "veg"),
            ("Palak Nadur", "veg"),
        ],
        "Non-Vegetarian Entrees": [
            ("Mutton Roganjosh", "non-veg"),
            ("Masc", "non-veg"),
            ("Mutton Yakhni", "non-veg"),
            ("Mutton Kaliya", "non-veg"),
            ("Chicken Yakhni", "non-veg"),
            ("Chicken Roganjosh", "non-veg"),
            ("Gaad with Vegetables", "non-veg"),
            ("Tchok Charwan", "non-veg"),
        ],
        "Wazwan": [
            ("Tamatar Tchaman", "veg"),
            ("Mutton Rista", "non-veg"),
            ("Mutton Goshtaba", "non-veg"),
            ("Mutton Marchwangan Korma", "non-veg"),
            ("Harissa", "non-veg"),
            ("Waza Kokur", "non-veg"),
            ("Chicken Marchwangan Korma", "non-veg"),
            ("Chicken Dhaniwal Korma", "non-veg"),
            ("Methi Maaz", "non-veg"),
        ],
        "Breads & Bakehouse": [
            ("Kashmiri Kulcha", "veg"),
            ("Desi Ghee Kulcha", "veg"),
            ("Lavasa", "veg"),
            ("Girda / Tchot", "veg"),
            ("Katlam", "veg"),
            ("Telvor", "veg"),
            ("Sheermal", "veg"),
            ("Bagherkhani", "veg"),
            ("Madur Khatayi", "veg"),
            ("Gyev Tchot", "veg"),
            ("Routh", "veg"),
        ]
    }
    
    created_items = 0
    for cat_name, items in menu_data.items():
        # Get or create category (use created_by=1, assume admin user id=1 exists)
        category = db.query(Category).filter_by(name=cat_name).first()
        if not category:
            category = Category(name=cat_name, created_by=1)
            db.add(category)
            db.flush()  # Get id
        cat_id = category.id
        
        # Add items if not exist (unique by name+category)
        for item_name, item_type in items:
            existing = db.query(MenuItem).filter_by(name=item_name.strip(), category_id=cat_id).first()
            if not existing:
                menu_item = MenuItem(
                    name=item_name.strip(),
                    category_id=cat_id,
                    type=item_type
                )
                db.add(menu_item)
                created_items += 1
    
    db.commit()
    return f"Successfully seeded {created_items} new menu items."

