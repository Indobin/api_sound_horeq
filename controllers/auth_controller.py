from fastapi import HTTPException
from models.akun_models import RegisterModel, LoginModel, UpdateAkuntModel
from app.supabase_client import supabase
from passlib.context import CryptContext
from jose import jwt
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def has_password(password: str)->str:
 return pwd_context.hash(password)

def verify_password(password: str, hashed:str)-> bool:
 return pwd_context.verify(password, hashed)

def create_token(data: dict):
 return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def register_akun(user: RegisterModel):
 cek = supabase.table("akun").select("id").eq("email", user.email).execute()
 if cek.data:
  raise HTTPException(
   status_code=400,
   detail="Email sudah terdaftar"
  )
 hashed_pw = has_password(user.password)
 created = user.created_at or datetime.utcnow()
 result = supabase.table("akun").insert({
  "username": user.username,
  "email": user.email,
  "password": hashed_pw,
  "status": user.status,
  "nama": user.nama,
  "no_hp": user.no_hp,
  "created_at": created.isoformat()
 }).execute()
 return {
  "messege": "Registrasi berhasil",
  "akun": result.data[0]
 }
 
def login_akun(user: LoginModel):
    cekAkun = supabase.table("akun").select("*").eq("email", user.email).single().execute()

    if not cekAkun.data:
        raise HTTPException(
            status_code=404,
            detail="Akun tidak ditemukan"
        )

    akun = cekAkun.data  # ⬅️ akun dari Supabase, tetap pisah dari `user`

    if not verify_password(user.password, akun["password"]):
        raise HTTPException(
            status_code=401,
            detail="Password salah"
        )

    token = create_token({
        "id": akun["id"],
        "email": akun["email"],
        "status": akun["status"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

def edit_profile(akun_db: dict, data:UpdateAkuntModel):
  update_dict = {}

  if data.username is not None:
    update_dict["username"] = data.username
  if data.email is not None:
    exist = supabase.table("akun").select("id")\
      .eq("email", data.email).neq("id", akun_db["id"]).execute()
    if exist.data:
      raise HTTPException(
        status_code=400,
        detail="Email sudah dipakai"
      )
    update_dict["email"] = data.email
  if data.password is not None:
    update_dict["password"] = has_password(data.password)
  if data.nama is not None:
    update_dict["nama"] = data.nama
  if data.no_hp is not None:
    update_dict["no_hp"] = data.no_hp
  if not update_dict:                # tidak ada yang diubah
    raise HTTPException(
        status_code=400,
        detail="Tidak ada data diperbarui"
    )

  result = supabase.table("akun").update(update_dict).eq("id", akun_db["id"]).execute()
  return {
    "messege": "Profil berhasil diperbarui",
    "akun": result.data[0]}