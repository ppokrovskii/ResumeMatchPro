from datetime import datetime
from pydantic import BaseModel, Field

class CreateUserRequest(BaseModel):
    userId: str
    email: str
    name: str
    isAdmin: bool = False
    filesLimit: int = 20
    matchingLimit: int = 100

class CreateUserResponse(BaseModel):
    userId: str
    email: str
    name: str
    isAdmin: bool
    filesLimit: int
    matchingLimit: int
    matchingUsedCount: int = 0
    filesCount: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class UserDb(BaseModel):
    """Database model for user"""
    userId: str
    email: str
    name: str
    isAdmin: bool
    filesLimit: int
    matchingLimit: int
    matchingUsedCount: int = 0
    filesCount: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    lastMatchingReset: datetime = Field(default_factory=datetime.utcnow)

class UpdateUserLimitsRequest(BaseModel):
    userId: str
    filesLimit: int
    matchingLimit: int 