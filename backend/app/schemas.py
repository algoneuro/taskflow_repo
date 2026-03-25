from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, Dict
import re

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    
    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers and underscore')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Task schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field("pending", pattern="^(pending|in_progress|completed)$")
    priority: Optional[int] = Field(1, ge=1, le=3)
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")
    priority: Optional[int] = Field(None, ge=1, le=3)
    due_date: Optional[datetime] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Statistics schemas
class TasksSummaryResponse(BaseModel):
    total: int
    by_status: Dict[str, int]
    avg_priority: float
    completion_rate: float
    workload_score: int

class PriorityDistributionResponse(BaseModel):
    distribution: Dict[str, int]
    percentages: Dict[str, float]