from datetime import datetime, UTC
from typing import Annotated, Optional
from pydantic import BaseModel, Field, PlainSerializer

# Create a custom datetime type that serializes to ISO format
DateTimeISO = Annotated[
    datetime,
    PlainSerializer(lambda dt: dt.isoformat(), return_type=str)
]

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
    createdAt: DateTimeISO = Field(default_factory=lambda: datetime.now(UTC))

class UserDb(BaseModel):
    """Database model for user"""
    id: str = Field(default=None)
    userId: str
    email: str
    name: str
    isAdmin: bool = False
    filesLimit: int = 20
    matchingLimit: int = 100
    matchingUsedCount: int = 0
    filesCount: int = 0
    createdAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    lastMatchingReset: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        populate_by_name = True
        
    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        # Ensure all datetime fields are timezone-aware
        if not data['createdAt'].tzinfo:
            data['createdAt'] = data['createdAt'].replace(tzinfo=UTC)
        if not data['lastMatchingReset'].tzinfo:
            data['lastMatchingReset'] = data['lastMatchingReset'].replace(tzinfo=UTC)
            
        # Convert datetime objects to ISO format strings
        data['createdAt'] = data['createdAt'].isoformat()
        data['lastMatchingReset'] = data['lastMatchingReset'].isoformat()
        
        # Use the provided id if it exists, otherwise use userId
        if 'id' in kwargs.get('exclude', set()):
            data.pop('id', None)
        else:
            data['id'] = data.get('id') or data['userId']
        
        return data

    def model_post_init(self, __context) -> None:
        # Set id to the provided value or userId
        if not self.id:
            self.id = self.userId
            
        # Ensure datetime fields are timezone-aware
        if not self.createdAt.tzinfo:
            self.createdAt = self.createdAt.replace(tzinfo=UTC)
        if not self.lastMatchingReset.tzinfo:
            self.lastMatchingReset = self.lastMatchingReset.replace(tzinfo=UTC)

class UpdateUserLimitsRequest(BaseModel):
    userId: str
    filesLimit: int
    matchingLimit: int 