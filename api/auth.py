from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# To get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context with fallback schemes
try:
    # First try with bcrypt
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Test it to see if it works
    pwd_context.hash("test")
    logger.info("Using bcrypt for password hashing")
except Exception as e:
    logger.warning(f"Bcrypt error: {e}")
    # Fall back to sha256_crypt if bcrypt fails
    logger.info("Falling back to sha256_crypt for password hashing")
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# This will be initialized with users from environment variables
# Format: username1:password1,username2:password2
USERS = {}

# Load users from environment
def load_users():
    users_env = os.getenv("AUTH_USERS", "admin:password")
    logger.info(f"Loading users from environment: {users_env.split(',')[0].split(':')[0]}...")
    user_pairs = users_env.split(",")
    for user_pair in user_pairs:
        if ":" in user_pair:
            username, password = user_pair.split(":", 1)
            # Store hashed password
            USERS[username] = pwd_context.hash(password)

# OAuth2 password bearer for token retrieval
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in USERS:
        return UserInDB(username=username, hashed_password=USERS[username])
    return None

def authenticate_user(username: str, password: str):
    user = get_user(None, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(None, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Initialize users on module import
load_users()