from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

# SQLite-specific configuration
connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    from sqlalchemy.pool import NullPool
    connect_args = {
        "check_same_thread": False,
        "timeout": 30.0,
        "isolation_level": None  # autocommit mode
    }
    # Use NullPool - creates new connection per request
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        poolclass=NullPool,
        echo=False
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=False,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

