from .base import HTTPException, supabase, datetime
from .base import CreateEventModel, UploadFile
# import aiofiles
async def event_peserta(akun: dict):
    # Cek role peserta
    if akun.get("role_akun_id") != 2:
        raise HTTPException(status_code=403, detail="Hanya peserta yang dapat mengakses data ini.")

    try:
        response = (
            supabase
            .table("event")
            .select("id, judul, tanggal_event, jam_mulai, lokasi, harga_tiket, tipe_tiket, foto_url")
            .is_("deleted_at", None)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
async def eventId_peserta(event_id: int, akun: dict):
    
    if akun.get("role_akun_id") != 2:
        raise HTTPException(status_code=403, detail="Hanya peserta yang dapat mengakses data ini.")

    try:
        response = (
            supabase
            .table("event")
            .select("id, judul, deskripsi, tanggal_event, jam_mulai, lokasi, harga_tiket, foto_url, tipe_tiket, jumlah_tiket, latitude, longitude")
            .eq("id", event_id)
            .is_("deleted_at", None)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Event tidak ditemukan")

        return {"data": response.data}

    except Exception as e:
      
        raise HTTPException(status_code=500, detail=str(e))

async def event_penyelenggara(akun: dict):
    if akun.get("role_akun_id") != 1:
        raise HTTPException(status_code=403, detail="Hanya penyelenggara yang dapat mengakses data ini.")

    try:
        response = (
            supabase
            .table("event")
            .select("id, judul, deskripsi, tanggal_event, jam_mulai, lokasi, harga_tiket, foto_url, tipe_tiket")
            .eq("akun_id", akun["id"])
            .is_("deleted_at", None)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

MAX_FILE_SIZE_MB = 1

async def create_event(akun: dict, data: CreateEventModel, foto: UploadFile):
    try:
        if akun.get("role_akun_id") != 1:
            raise HTTPException(status_code=403, detail="Hanya penyelenggara yang dapat membuat event")
        created = datetime.utcnow()

        # Validasi
        if data.tanggal_event < datetime.now().date():
            raise HTTPException(status_code=400, detail="Tanggal event tidak boleh di masa lalu")


        if data.harga_tiket is not None and data.harga_tiket < 0:
            raise HTTPException(status_code=400, detail="Harga tiket tidak boleh negatif")
        
        content = await foto.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Ukuran foto maksimal 1MB")
    # Upload ke Supabase Storage
        filename = f"{akun['id']}_{int(datetime.utcnow().timestamp())}.{foto.filename.split('.')[-1]}"
        upload_result = supabase.storage.from_("event-foto").upload(filename, content, {
            "content-type": foto.content_type
        })

        if hasattr(upload_result, 'error') and upload_result.error:
            raise HTTPException(status_code=500, detail="Upload foto gagal")

        public_url = supabase.storage.from_("event-foto").get_public_url(filename)


        # Simpan event
        event_data = {
            "judul": data.judul,
            "deskripsi": data.deskripsi,
            "tanggal_event": data.tanggal_event.isoformat(),
            "jam_mulai": data.jam_mulai.isoformat(),
            "durasi_event": data.durasi_event,
            # "harga_tiket": float(data.harga_tiket),
            "jumlah_tiket": data.jumlah_tiket,
            "tipe_tiket": data.tipe_tiket,  
            "lokasi": data.lokasi,
            "latitude": data.latitude,
            "longitude": data.longitude,
            "foto_url": public_url,
            "akun_id": akun["id"],
            "created_at": created.isoformat(),
            "harga_tiket": float(data.harga_tiket) if data.harga_tiket is not None else 0.0
        }
    
        response = supabase.table("event").insert(event_data).execute()

        # if not response.data:
        #     raise HTTPException(status_code=500, detail="Gagal menyimpan event")
        
        return {"message": "Event berhasil dibuat", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")