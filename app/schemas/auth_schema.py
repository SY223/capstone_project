from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RefreshTokenSchema(BaseModel):
    refresh_token: str

class LogoutSchema(BaseModel):
    refresh_token: str

class PasswordResetRequestSchema(BaseModel):
    email: EmailStr

class PasswordResetConfirmSchema(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8)

class VerifyEmailSchema(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)

    model_config = ConfigDict(from_attributes=True)