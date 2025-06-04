from .base import APIRouter, Depends, CreateEventModel, get_current_akun,UploadFile, File, Form, FastAPI, Optional
from .base import create_event, event_penyelenggara
from .base import event_peserta, eventId_peserta
from datetime import date, datetime
from decimal import Decimal
router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("/peserta")
async def get_event_peserta(
 akun: dict = Depends(get_current_akun)
 ):
 return await event_peserta(akun)
   
@router.get("/peserta/{id}")   
async def getId_event_peserta(
 event_id: int, 
 akun: dict = Depends(get_current_akun)
 ):
 return await eventId_peserta(event_id, akun)
   
@router.get("/penyelenggara")
async def get_event_penyelenggara(
 akun: dict = Depends(get_current_akun)
 ):
 return await event_penyelenggara(akun)
      
   
@router.post("/create")
async def create_event_penyelenggara(
 akun: dict = Depends(get_current_akun),
 judul: str = Form(...),
 deskripsi: str = Form(...),
 tanggal_event: date = Form(...),
 jam_mulai: str = Form(...),
 durasi_event: int = Form(...),
 harga_tiket: Optional[str] = Form(None),
 jumlah_tiket: int = Form(...),
 tipe_tiket: int = Form(...),
 lokasi: str = Form(...),
 latitude: float = Form(...),
 longitude: float = Form(...),
 foto: UploadFile = File(...)
 ):
 harga_decimal = Decimal(harga_tiket) if harga_tiket else None
 data = CreateEventModel(
        
        judul=judul,
        deskripsi=deskripsi,
        tanggal_event=tanggal_event,
        jam_mulai=datetime.strptime(jam_mulai, "%H:%M:%S").time(),
        durasi_event=durasi_event,
        harga_tiket=harga_decimal,
        jumlah_tiket=jumlah_tiket,
        tipe_tiket=tipe_tiket,
        lokasi=lokasi,
        latitude=latitude,
        longitude=longitude,
    )

 return await create_event(akun, data, foto)