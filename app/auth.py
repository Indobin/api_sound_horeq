from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from app.supabase_client import supabase

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM  = "HS256"

bearer_scheme = HTTPBearer()

def get_current_akun(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        akun_id: int = payload.get("id")
        if akun_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token tidak valid")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token tidak valid / kedaluwarsa")
    res = supabase.table("akun").select("*").eq("id", akun_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Akun tidak ditemukan")
    return res.data       
