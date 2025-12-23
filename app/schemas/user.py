from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Pydantic V2 config (from_attributes=True replaces orm_mode=True)
    model_config = ConfigDict(from_attributes=True)
