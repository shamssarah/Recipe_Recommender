# from app import app
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import APIRouter, HTTPException, status

# CRITICAL: This allows the HTML file running on a browser port (e.g., file:// or localhost:3000)
# to communicate with the FastAPI server (localhost:8000).
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://127.0.0.1:8000",
#     "http://127.0.0.1:5500", # Common VSCode Live Server port
#     "*", # In development, using '*' is common for testing
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Initialize the APIRouter instead of FastAPI
router = APIRouter(
    prefix="/users",  # All routes in this router will start with /users
    tags=["users", "auth"]
)

# # --- 2. Pydantic Models (Mirroring your data structure) ---

class UserBase(BaseModel):
    username: str = Field(..., min_length=3)
    email: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime

class UserPublic(UserBase):
    id: int
    created_at: datetime
    # We never return the password or hashed_password

class LoginPayload(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int

# --- 3. In-Memory "Database" (Replacing SQLAlchemy for simplicity) ---

_user_db: Dict[int, UserDB] = {}
_next_user_id = 1

# --- 4. Mock Authentication Functions ---

def hash_password(password: str) -> str:
    """Mock password hashing - NEVER use this in production!"""
    return f"Hashed::{password}::{len(password)}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Mock password verification"""
    return hashed_password == hash_password(plain_password)

def get_user_by_username(username: str) -> Optional[UserDB]:
    """Retrieves user by username from the mock DB"""
    for user in _user_db.values():
        if user.username == username:
            return user
    return None

# --- 5. FastAPI Endpoints ---

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate):
    """Registers a new user."""
    global _next_user_id
    
    if get_user_by_username(payload.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Mock the DB entry creation
    user_id = _next_user_id
    hashed_password = hash_password(payload.password)
    
    new_user = UserDB(
        id=user_id,
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )
    
    _user_db[user_id] = new_user
    _next_user_id += 1
    
    # Return a clean public model
    return new_user

@router.post("/login", response_model=TokenResponse)
async def login_user(payload: LoginPayload):
    """Authenticates a user and returns a token."""
    user = get_user_by_username(payload.username)

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In a real app, this would be a secure JWT token
    access_token = str(uuid.uuid4()) 
    
    return TokenResponse(access_token=access_token, user_id=user.id)

@router.get("/status")
async def get_status():
    """Endpoint to check if the server is running and how many users exist."""
    return {"status": "ok", "users_registered": len(_user_db)}