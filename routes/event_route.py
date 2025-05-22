from .base import APIRouter, Depends, CreateEventModel, get_current_akun,UploadFile, File, Form, FastAPI
from .base import create_event, event_penyelenggara
from .base import event_peserta, eventId_peserta
from datetime import date, datetime

router = APIRouter()

@router.get("/event/peserta")
async def get_event_peserta(
 akun: dict = Depends(get_current_akun)
 ):
 return await event_peserta(akun)
   
@router.get("/event/peserta/{id}")   
async def getId_event_peserta(
 event_id: int, 
 akun: dict = Depends(get_current_akun)
 ):
 return await eventId_peserta(event_id, akun)
   
@router.get("/event/penyelenggara")
async def get_event_penyelenggara(
 akun: dict = Depends(get_current_akun)
 ):
 return await event_penyelenggara(akun)
      
   
@router.post("/event")
async def create_event_penyelenggara(
 akun: dict = Depends(get_current_akun),
 judul: str = Form(...),
 deskripsi: str = Form(...),
 tanggal_event: date = Form(...),
 jam_mulai: str = Form(...),
 durasi_event: int = Form(...),
 harga_tiket: float = Form(...),
 jumlah_tiket: int = Form(...),
 tipe_tiket: int = Form(...),
 lokasi: str = Form(...),
 latitude: float = Form(...),
 longitude: float = Form(...),
 foto: UploadFile = File(...)
 ):
 data = CreateEventModel(
        judul=judul,
        deskripsi=deskripsi,
        tanggal_event=tanggal_event,
        jam_mulai=datetime.strptime(jam_mulai, "%H:%M").time(),
        durasi_event=durasi_event,
        harga_tiket=harga_tiket,
        jumlah_tiket=jumlah_tiket,
        tipe_tiket=tipe_tiket,
        lokasi=lokasi,
        latitude=latitude,
        longtitude=longitude,
    )

 return await create_event(akun, data, foto)