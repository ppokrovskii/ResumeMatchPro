from datetime import datetime
from typing import Annotated
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
    createdAt: DateTimeISO = Field(default_factory=datetime.utcnow)

class UserDb(BaseModel):
    """Database model for user"""
    id: str = Field(default=None)  # Will be set to userId in model_config
    userId: str
    email: str
    name: str
    isAdmin: bool = False
    filesLimit: int = 20
    matchingLimit: int = 100
    matchingUsedCount: int = 0
    filesCount: int = 0
    createdAt: DateTimeISO = Field(default_factory=datetime.utcnow)
    lastMatchingReset: DateTimeISO = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True
    }

    def model_post_init(self, __context) -> None:
        if self.id is None:
            self.id = self.userId

class UpdateUserLimitsRequest(BaseModel):
    userId: str
    filesLimit: int
    matchingLimit: int 