from fastapi import APIRouter, Depends
from models.akun_models import RegisterModel, LoginModel, UpdateAkuntModel
from controllers.auth_controller import register_akun, login_akun, edit_profile
from app.auth import get_current_akun

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: RegisterModel):
 return register_akun(user)

@router.post("/login")
def login(user: LoginModel):
 return login_akun(user)

@router.put("/profile")
def update_profile(
 data: UpdateAkuntModel,
 akun: dict = Depends(get_current_akun)
):
 return edit_profile(akun, data)