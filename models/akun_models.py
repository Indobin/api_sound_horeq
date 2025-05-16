from pydantic import BaseModel, EmailStr, constr
from enum import Enum
class AkunRole(str, Enum):
 penyelenggara = 'penyelenggara'
 peserta = 'peserta'
 
class RegisterModel(BaseModel):
    username: constr(min_length=3, max_length=30)
    password: constr(min_length=8)
    email: EmailStr
    status: AkunRole
    nama: constr(min_length=3, max_length=100)
    no_hp: constr(min_length=10, max_length=15)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "satya123",
                "password": "securePassword123",
                "email": "satya@example.com",
                "status": "penyelenggara",
                "nama": "Satya Bintang",
                "no_hp": "081234567890"
            }
        }

class LoginModel(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "satya@example.com",
                "password": "securePassword123"
            }
        }
