from fastapi import HTTPException
from models.akun_models import RegisterModel, LoginModel, UpdateAkuntModel
from app.supabase_client import supabase
from passlib.context import CryptContext
from jose import jwt
import os
from dotenv import load_dotenv
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import codecs
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

# Kunci AES dalam format string heksadesimal (64 karakter = 32 bytes)
AES_KEY_HEX = os.getenv("AES_KEY_HEX")

# Konversi string heksadesimal menjadi bytes yang sebenarnya
try:
    AES_KEY = codecs.decode(AES_KEY_HEX, 'hex')
except Exception as e:
    raise ValueError(f"Gagal mengonversi kunci AES heksadesimal: {e}")

# Verifikasi panjang kunci dalam bytes
if len(AES_KEY) not in [16, 24, 32]:
    raise ValueError(f"Panjang kunci AES tidak valid: {len(AES_KEY)} bytes. Harus 16, 24, atau 32 bytes.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def pad(data: bytes) -> bytes:
    """Menambahkan padding ke data agar sesuai dengan blok AES (16 bytes)."""
    padding = 16 - (len(data) % 16)
    return data + bytes([padding] * padding)

def unpad(data: bytes) -> bytes:
    """Menghapus padding dari data setelah dekripsi."""
    padding_len = data[-1]
    # Periksa apakah padding valid untuk mencegah serangan padding oracle
    if padding_len < 1 or padding_len > 16 or not all(data[i] == padding_len for i in range(len(data) - padding_len, len(data))):
        raise ValueError("Padding tidak valid atau rusak")
    return data[:-padding_len]

def encrypt_data_aes(data: str) -> str: # Mengubah tipe input menjadi str
    """Mengenkripsi string data menggunakan AES dalam mode CBC."""
    # Pastikan data yang akan dienkripsi adalah bytes
    data_bytes = data.encode('utf-8')
    iv = get_random_bytes(16) # Inisialisasi Vektor (IV) harus acak untuk setiap enkripsi
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    padded_data = pad(data_bytes)
    encrypted_data = cipher.encrypt(padded_data)
    # Menggabungkan IV dengan data terenkripsi dan melakukan base64 encode
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

def decrypt_data_aes(encoded_data: str) -> str: # Mengubah nama parameter menjadi encoded_data
    """Mendekripsi string data yang dienkripsi AES."""
    try:
        raw = base64.b64decode(encoded_data)
    except Exception as e:
        raise ValueError(f"Data Base64 tidak valid: {e}")

    if len(raw) < 16:
        raise ValueError("Data terenkripsi terlalu pendek untuk berisi IV")

    iv = raw[:16] # Ambil IV dari 16 byte pertama
    encrypted_payload = raw[16:] # Sisa adalah data terenkripsi

    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted_padded_data = cipher.decrypt(encrypted_payload)
    
    return unpad(decrypted_padded_data).decode('utf-8')

def has_password(password: str)->str:
 return pwd_context.hash(password)

def verify_password(password: str, hashed:str)-> bool:
 return pwd_context.verify(password, hashed)

def create_token(data: dict):
 return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def register_akun(user: RegisterModel):
 cek = supabase.table("akun").select("id").eq("email", user.email).execute()
 cek1 = supabase.table("akun").select("id").eq("username", user.username).execute()
 if cek.data:
  raise HTTPException(
   status_code=400,
   detail="Email sudah terdaftar"
  )
 if cek1.data:
  raise HTTPException(
   status_code=400,
   detail="Username sudah terdaftar"
  )
 hashed_pw = has_password(user.password)
 created = datetime.utcnow()

 nama_encrypted = encrypt_data_aes(user.nama)
 hp_encrypted = encrypt_data_aes(user.no_hp)
 result = supabase.table("akun").insert({
  "username": user.username,
  "email": user.email,
  "password": hashed_pw,
  "role_akun_id": user.role_akun,
  "nama": nama_encrypted,
  "no_hp": hp_encrypted,
  "created_at": created.isoformat()
 }).execute()
 return {
  "messege": "Registrasi berhasil",
  "akun": result.data[0]
 }
 
def login_akun(user: LoginModel):
    cekAkun = supabase.table("akun").select("*").eq("username", user.username).single().execute()

    if not cekAkun.data:
        raise HTTPException(
            status_code=404,
            detail="Akun tidak ditemukan"
        )

    akun = cekAkun.data 

    if not verify_password(user.password, akun["password"]):
        raise HTTPException(
            status_code=401,
            detail="Password salah"
        )
    nama = decrypt_data_aes(akun["nama"])
    no_hp = decrypt_data_aes(akun["no_hp"])
    token = create_token({
        "id": akun["id"],
        "username": akun["username"],
        "no_hp": no_hp,
        "nama": nama,
        "email": akun["email"],
        "role_akun_id": akun["role_akun_id"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "id": akun["id"],
        "username": akun["username"],
        "no_hp": akun["no_hp"],
        "nama": akun["nama"],
        "email": akun["email"],
        "role_akun_id": akun["role_akun_id"]
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