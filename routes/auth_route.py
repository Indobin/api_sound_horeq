from fastapi import APIRouter
from models.akun_models import RegisterModel, LoginModel
from controllers.auth_controller import register_akun, login_akun

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: RegisterModel):
 return register_akun(user)

@router.post("/login")
def login(user: LoginModel):
 return login_akun(user)