from .base import APIRouter, Depends, CreateEventModel, UpdateEventModel, get_current_akun,UploadFile, File, Form, FastAPI, Optional, Query
from .base import create_event, event_penyelenggara, update_event, eventId_penyelenggara
from .base import event_peserta, eventId_peserta, lokasi_event
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
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

@router.get("/penyelenggara/{event_id}")
async def get_event_detail(
  event_id: int, 
  akun: dict = Depends(get_current_akun)
  ):
 return await eventId_penyelenggara(event_id, akun)

@router.post("/create")
async def create_event_penyelenggara(
 akun: dict = Depends(get_current_akun),
 judul: str = Form(...),
 deskripsi: str = Form(...),
 tanggal_event: date = Form(...),
 jam_mulai: str = Form(...),
 durasi_event: int = Form(...),
 harga_tiket: Optional[str] = Form(0.0),
 jumlah_tiket: int = Form(...),
 tipe_tiket: int = Form(...),
 lokasi: str = Form(...),
 latitude: float = Form(...),
 longitude: float = Form(...),
 foto: UploadFile = File(...)
 ):
 harga_decimal = Decimal(harga_tiket) if harga_tiket else 0.0
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
def clean_optional_field(val):
    return val if val not in ("", None) else None
@router.put("/update/{event_id}")
async def update_event_route(
    event_id: int,
    akun: dict = Depends(get_current_akun),
    judul: Optional[str] = Form(None),
    deskripsi: Optional[str] = Form(None),
    tanggal_event: Optional[date] = Form(None),
    jam_mulai: Optional[str] = Form(None),
    durasi_event: Optional[int] = Form(None),
    harga_tiket: Optional[str] = Form(None),
    jumlah_tiket: Optional[int] = Form(None),
    tipe_tiket: Optional[int] = Form(None),
    lokasi: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    foto: Optional[UploadFile] = File(None)
):
    return await update_event(event_id, akun, judul, deskripsi, tanggal_event, jam_mulai, durasi_event,
                              harga_tiket, jumlah_tiket, tipe_tiket,
                              lokasi, latitude, longitude, foto)


    # return await update_event(event_id, akun, form_data, foto)
@router.get("/lokasi-event")
async def lokasi(
    akun: dict = Depends(get_current_akun)
):
    return await lokasi_event(akun)



 