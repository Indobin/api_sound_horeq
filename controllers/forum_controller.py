from .base import HTTPException, supabase,  datetime, os
from .base import CreateForumModels
import pytz
from dateutil import parser


async def forum_chat(data: CreateForumModels, akun: dict):
 try:
  wib = pytz.timezone("Asia/Jakarta")
  waktu_wib = datetime.now(wib)
  response = (
   supabase
   .table("forum")
   .insert({
    "akun_id": akun['id'],
    "username": akun['username'],
    "pesan": data.pesan,
    "created_at": waktu_wib.isoformat()
   }).execute()
  )
  return {
       "message": "Pesan berhasil dikirim",
       "data": response.data
       
   }
 except Exception as e:
  raise HTTPException(
   status_code= 500,
   detail= str(e)
  )
  
async def get_forum_chat(akun: dict):
 try:
  response = (
   supabase
   .table("forum")
   .select("username", "pesan", "created_at")
   .order("created_at", desc=True)
   .execute()
  )
  data = response.data
  for item in data:
   created_at = item.get("created_at")
   if created_at:
      dt = parser.parse(created_at)
      item["tanggal"] = dt.strftime("%Y-%m-%d")
      item["waktu"] = dt.strftime("%H:%M")
  return data
 except Exception as e:
  raise HTTPException(
   status_code= 500,
   detail= str(e)
  )