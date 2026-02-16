"""
Initialise database with default categories
"""
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.database import Category

logger = logging.getLogger("memorybook")

# Create tables
Base.metadata.create_all(bind=engine)

# Default categories
DEFAULT_CATEGORIES = [
    {"name": "Receipts", "description": "Receipts from memorable trips and purchases", "color": "#10b981"},
    {"name": "Certificates", "description": "Certificates and awards", "color": "#f59e0b"},
    {"name": "School Photos", "description": "School photos and yearbooks", "color": "#3b82f6"},
    {"name": "Others", "description": "Other memories", "color": "#8b5cf6"},
]


def init_default_categories():
    """Create default categories if they don't exist"""
    db: Session = SessionLocal()
    try:
        for cat_data in DEFAULT_CATEGORIES:
            existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not existing:
                category = Category(**cat_data)
                db.add(category)
                logger.info("Created category: %s", cat_data["name"])
        db.commit()
        logger.info("Database initialised successfully!")
    except Exception as e:
        logger.error("Error initialising database: %s", e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_default_categories()

