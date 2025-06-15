from .base import HTTPException, supabase, jwt, load_dotenv, datetime, UploadFile 
from models.akun_models import RegisterModel, LoginModel, UpdateAkuntModel
from passlib.context import CryptContext
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import codecs
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
        # "no_hp": no_hp,
        # "nama": nama,
        "email": akun["email"],
        "role_akun_id": akun["role_akun_id"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "id": akun["id"],
        "username": akun["username"],
        "no_hp": no_hp,
        "nama": nama,
        "email": akun["email"],
        "role_akun_id": akun["role_akun_id"],
        "foto_url": akun["profil_url"]
    }

MAX_FILE_SIZE_MB = 1
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
SUPABASE_BUCKET = "foto-profil"
async def edit_profile(akun_db: dict, data:UpdateAkuntModel, foto: UploadFile = None):
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
  
  profile_url = None
  if foto:
    try:
      content = await foto.read()
      if len(content) > MAX_FILE_SIZE_BYTES:
         raise HTTPException(
            status_code=400,
            detail=f"Ukuran foto maksimal {MAX_FILE_SIZE_MB}MB"
         )
      file_extension = foto.filename.split(".")[-1]
      filename = f"{akun_db['id']}_{int(datetime.utcnow().timestamp())}.{file_extension}"

      upload_result = supabase.storage.from_(SUPABASE_BUCKET).upload(
         filename,
         content,
         {"content-type": foto.content_type}
      )
      if upload_result and upload_result.get("error"):
         raise HTTPException(
            status_code=500,
            detail=f"Upload foto gagal: {upload_result['error'].get('message', 'Unknown error')}"
         )
      
      public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
      update_dict["profil_url"] = public_url
    except HTTPException:
      raise
    except Exception as e:
        print(f"Error processing photo upload: {e}")
        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan saat mengunggah foto profil"
        )
  if not update_dict:               
    raise HTTPException(
        status_code=400,
        detail="Tidak ada data atau foto yang diperbarui"
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

  final_photo_url = updated_akun.get("profil_url", None)


  return {
    "messege": "Profil berhasil diperbarui",
    "akun": result.data[0]}

