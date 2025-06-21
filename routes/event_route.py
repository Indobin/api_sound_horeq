from .base import APIRouter, Depends, CreateEventModel, get_current_akun,UploadFile, File, Form, FastAPI, Optional, Query
from .base import create_event, event_penyelenggara, update_event
from .base import event_peserta, eventId_peserta, melihat_lokasi_peserta
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

@router.put("/update/{event_id}")
async def update_event_penyelenggara(
    event_id: int,
    akun: dict = Depends(get_current_akun),
    judul: str = Form(...),
    deskripsi: str = Form(...),
    tanggal_event: date = Form(...),
    jam_mulai: str = Form(...),
    durasi_event: int = Form(...),
    harga_tiket: Optional[str] = Form(None),  # Ubah default menjadi None
    jumlah_tiket: int = Form(...),
    tipe_tiket: int = Form(...),
    lokasi: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    foto: Optional[UploadFile] = File(None)
):
    # Konversi harga tiket ke Decimal
    harga_decimal = Decimal(harga_tiket) if harga_tiket is not None else 0.0  # Periksa None
    
    # Buat model data event
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

    return await update_event(event_id, akun, data, foto)

@router.get("/melihat_lokasi_peserta")
async def melihat_lokasi_peserta_endpoint(
    latitude: float = Query(..., description="Koordinat latitude"),
    longitude: float = Query(..., description="Koordinat longitude"),
    lokasi: str = Query(..., description="Alamat lokasi"),
    akun: dict = Depends(get_current_akun)
):
    return await melihat_lokasi_peserta(akun, latitude, longitude, lokasi)