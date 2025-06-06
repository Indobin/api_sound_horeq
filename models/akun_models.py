from .base import BaseModel, EmailStr, constr,  Optional

 
class RegisterModel(BaseModel):
    username: constr(min_length=3, max_length=30)
    password: constr(min_length=8)
    email: EmailStr
    role_akun: int
    nama: constr(min_length=3, max_length=100)
    no_hp: constr(min_length=10, max_length=15)
    class Config:
        json_schema_extra = {
            "example": {
                "username": "satya123",
                "password": "securePassword123",
                "email": "satya@example.com",
                "role_akun": 1,
                "nama": "Satya Bintang",
                "no_hp": "081234567890",
            }
        }

class LoginModel(BaseModel):
    username: constr(min_length=5, max_length=30)
    password: constr(min_length=8)

    # class Config:
    #     json_schema_extra = {
    #         "example": {
    #             "email": "satya@example.com",
    #             "password": "securePassword123"
    #         }
    #     }

class UpdateAkuntModel(BaseModel):
    username: Optional[constr(min_length=3, max_length=30)] = None
    password: Optional[constr(min_length=8)] = None 
    email: Optional[EmailStr] = None    
    nama: Optional[constr(min_length=3, max_length=100)] = None
    no_hp: Optional[constr(min_length=10, max_length=15)] = None
