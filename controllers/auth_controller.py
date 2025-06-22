from .base import HTTPException, supabase, jwt, load_dotenv, datetime, UploadFile 
from models.akun_models import RegisterModel, LoginModel, UpdateAkuntModel
from passlib.context import CryptContext
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import codecs
from postgrest.exceptions import APIError

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

AES_KEY_HEX = os.getenv("AES_KEY_HEX")

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
    if padding_len < 1 or padding_len > 16 or not all(data[i] == padding_len for i in range(len(data) - padding_len, len(data))):
        raise ValueError("Padding tidak valid atau rusak")
    return data[:-padding_len]

def encrypt_data_aes(data: str) -> str:
    """Mengenkripsi string data menggunakan AES dalam mode CBC."""
    data_bytes = data.encode('utf-8')
    iv = get_random_bytes(16) 
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    padded_data = pad(data_bytes)
    encrypted_data = cipher.encrypt(padded_data)
    # Menggabungkan IV dengan data terenkripsi dan melakukan base64 encode
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

def decrypt_data_aes(encoded_data: str) -> str: 
    """Mendekripsi string data yang dienkripsi AES."""
    try:
        raw = base64.b64decode(encoded_data)
    except Exception as e:
        raise ValueError(f"Data Base64 tidak valid: {e}")

    if len(raw) < 16:
        raise ValueError("Data terenkripsi terlalu pendek untuk berisi IV")

    iv = raw[:16]
    encrypted_payload = raw[16:]

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
  "role_akun_id": user.role_akun_id,
  "nama": nama_encrypted,
  "no_hp": hp_encrypted,
  "profil_url": None,
  "created_at": created.isoformat()
 }).execute()
 return {
  "messege": "Registrasi berhasil",
  "akun": result.data[0]
 }
 
def login_akun(user: LoginModel):
    try:
      cekAkun = supabase.table("akun").select("*").eq("username", user.username).single().execute()
      akun = cekAkun.data
      if not akun:
          raise HTTPException(
              status_code=404,
              detail="Akun tidak ditemukan"
          )
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
          "email": akun["email"],
          "role_akun_id": akun["role_akun_id"]
      })

      return {
          "access_token": token,
          "token_type": "bearer",
          "id": akun["id"],
          "username": akun["username"],
          "password": akun["password"],
          "no_hp": no_hp,
          "nama": nama,
          "email": akun["email"],
          "role_akun_id": akun["role_akun_id"],
          "profil_url": akun["profil_url"]
      }
    except APIError as e:
      if e.code == "PGRST116":
          raise HTTPException(status_code=404, detail="Akun tidak ditemukan")
      raise HTTPException(status_code=500, detail="Terjadi kesalahan server")


async def edit_profile(akun_db: dict, data:UpdateAkuntModel):
  update_dict = {}

  if data.username is not None:
    cek_username = supabase.table("akun").select("id")\
    .eq("username", data.username).neq("id", akun_db["id"]).execute()
    if cek_username.data:
      raise HTTPException(
        status_code=400,
        detail="Username sudah dipakai"
      )
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
    update_dict["nama"] =  encrypt_data_aes(data.nama)
  if data.no_hp is not None:
    update_dict["no_hp"] = encrypt_data_aes(data.no_hp)
  
  if not update_dict:               
    raise HTTPException(
        status_code=400,
        detail="Tidak ada data yang diperbarui"
    )

  result = supabase.table("akun").update(update_dict).eq("id", akun_db["id"]).execute()
  
  if not result.data:
      raise HTTPException(
          status_code=500,
          detail="Gagal memperbarui profil di database"
      )
  updated_akun = result.data[0]
  updated_nama = decrypt_data_aes(updated_akun["nama"]) if updated_akun["nama"] else None
  updated_no_hp = decrypt_data_aes(updated_akun["no_hp"]) if updated_akun["no_hp"] else None

  

  new_token = create_token({
    "id": updated_akun["id"],
    "username": updated_akun["username"],
    "email": updated_akun["email"],
    "role_akun_id": updated_akun["role_akun_id"]
  })

  return {
    "messege": "Profil berhasil diperbarui",
    "access_token": new_token,
    "token_type": "bearer",
    "id": updated_akun["id"],
    "username": updated_akun["username"],
    "no_hp": updated_no_hp,
    "nama": updated_nama,
    "email": updated_akun["email"],
    "role_akun_id": updated_akun["role_akun_id"],
    "profile_photo_url": updated_akun.get("profil_url", None)
  }
MAX_FILE_SIZE_MB = 1
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
SUPABASE_BUCKET = "foto-profil"

async def edit_foto(akun_db: dict, foto: UploadFile):
    # Ambil foto lama jika ada
    akun_id = akun_db["id"]
    old_data = supabase.table("akun").select("profil_url").eq("id", akun_id).execute()

    old_url = old_data.data[0].get("profil_url") if old_data.data else None

    # Hapus foto lama dari storage jika ada
    if old_url:
      try:
          file_name = old_url.split("/")[-1].split("?")[0]
          delete_result = supabase.storage.from_(SUPABASE_BUCKET).remove([file_name])
          if isinstance(delete_result, list) and len(delete_result) > 0:
              print(f"✅ File lama berhasil dihapus: {file_name}")
          else:
              print("⚠️ Gagal menghapus file lama (atau tidak ditemukan)")
      except Exception as e:
        print(f"⚠️ Error parsing nama file lama: {e}")

    # Upload foto baru
    content = await foto.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Ukuran foto maksimal 2MB")

    file_ext = foto.filename.split(".")[-1]
    new_filename = f"{akun_id}_{int(datetime.utcnow().timestamp())}.{file_ext}"

    result = supabase.storage.from_(SUPABASE_BUCKET).upload(
        new_filename,
        content,
        {"content-type": foto.content_type}
    )

    if hasattr(result, "error") and result.error is not None:
        raise HTTPException(
            status_code=500,
            detail=f"Upload foto gagal: {result.error.message}"
        )
    public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(new_filename)

    update = supabase.table("akun").update({"profil_url": public_url}).eq("id", akun_id).execute()

    if not update.data:
        raise HTTPException(status_code=500, detail="Gagal menyimpan URL foto")

    return {
        "message": "Foto profil berhasil diperbarui",
        "profile_photo_url": public_url
    }
