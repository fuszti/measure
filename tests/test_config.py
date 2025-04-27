"""
Test configuration with database settings
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create a test database engine
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create test session
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create test tables
def setup_test_db():
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
def teardown_test_db():
    # Drop tables
    Base.metadata.drop_all(bind=test_engine)
    
    # Remove test.db file if exists
    if os.path.exists("./test.db"):
        os.remove("./test.db")