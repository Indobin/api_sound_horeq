from .base import APIRouter, Depends, register_akun, login_akun, edit_profile, get_current_akun,UploadFile, File
from .base import RegisterModel, LoginModel, UpdateAkuntModel, Optional

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register")
def register(user: RegisterModel):
 return register_akun(user)

@router.post("/login")
def login(user: LoginModel):
 return login_akun(user)

@router.put("/profile")
async def update_profile(
 data: UpdateAkuntModel,
 akun: dict = Depends(get_current_akun),
 foto: Optional[UploadFile] = File(None)
):
 return await edit_profile(akun, data, foto)

# @router.put("/foto")
# async def update_foto(
#  akun: dict = Depends(get_current_akun),
#  foto: UploadFile = File(...)
#  ):
#  return await edit_foto(akun, foto)