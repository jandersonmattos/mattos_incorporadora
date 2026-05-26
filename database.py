import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/incorporadora"
)

logger.info("Connecting to database: %s", DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL)

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,       # verify connections before use
        pool_recycle=300,         # recycle connections every 5 minutes
        connect_args={"connect_timeout": 10},
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.critical("Failed to create database engine: %s", e, exc_info=True)
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()