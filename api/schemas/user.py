from pydantic import BaseModel, Field
from datetime import datetime


class UserSignupRequest(BaseModel):
    password: str = Field(..., example="password")
    username: str = Field(..., example="admin")

    class Config:
        from_attributes = True
        
class UserInformationResponse(BaseModel):
    uuid: str
    username: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
        
class Token(BaseModel):
    access_token: str
    token_type: str