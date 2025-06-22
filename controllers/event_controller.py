from .base import HTTPException, supabase, datetime, Query
from .base import CreateEventModel, UploadFile
from typing import Optional

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

async def melihat_lokasi_peserta(akun: dict, latitude: float = Query(...), longitude: float = Query(...), lokasi: str = Query(...)):
   
    if not (-90 <= latitude <= 90):
        raise HTTPException(status_code=400, detail="Latitude harus antara -90 sampai 90")
    if not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Longitude harus antara -180 sampai 180")
    
    if len(lokasi.strip()) < 10: 
        raise HTTPException(status_code=400, detail="Alamat terlalu pendek (min 10 karakter)")

    return {
        "user_id": akun.get("id"),  
        "pesan": "Berikut lokasi yang Anda input:",
        "lokasi": {
            "alamat": lokasi,
            "koordinat": {
                "latitude": latitude,
                "longitude": longitude
            }
        },
        "catatan": "Berhasil mengambil data lokasi peserta."
    }

async def update_event(event_id: int, akun: dict, data: CreateEventModel, foto: Optional[UploadFile]):
    try:
        # Validasi role akun
        if akun.get("role_akun_id") != 1:
            raise HTTPException(status_code=403, detail="Hanya penyelenggara yang dapat mengedit event.")

        # Ambil event yang ada untuk verifikasi
        response_existing_event = (
            supabase
            .table("event")
            .select("akun_id, foto_url")
            .eq("id", event_id)
            .is_("deleted_at", None)
            .execute()
        )

        if hasattr(response_existing_event, 'error') and response_existing_event.error:
            raise HTTPException(status_code=500, detail=f"Gagal mengambil event untuk verifikasi: {response_existing_event.error.message}")

        if not response_existing_event.data:
            raise HTTPException(status_code=404, detail="Event tidak ditemukan.")

        existing_event = response_existing_event.data[0]

        if existing_event["akun_id"] != akun["id"]:
            raise HTTPException(status_code=403, detail="Anda tidak memiliki izin untuk mengedit event ini.")

        response_transactions = (
            supabase
            .table("transaksi")
            .select("id")
            .eq("event_id", event_id)
            .execute()
        )

        if hasattr(response_transactions, 'error') and response_transactions.error:
            raise HTTPException(status_code=500, detail=f"Gagal memeriksa transaksi: {response_transactions.error.message}")

        can_edit_all = not response_transactions.data  

        if data.tanggal_event < datetime.now().date():
            raise HTTPException(status_code=400, detail="Tanggal event tidak boleh di masa lalu.")

        if data.harga_tiket is not None and data.harga_tiket < 0:
            raise HTTPException(status_code=400, detail="Harga tiket tidak boleh negatif.")

        new_foto_url = existing_event["foto_url"]
        if foto:
            try:
                content = await foto.read()
                if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
                    raise HTTPException(status_code=400, detail=f"Ukuran foto maksimal {MAX_FILE_SIZE_MB}MB.")
                
                filename = f"{akun['id']}_{int(datetime.utcnow().timestamp())}.{foto.filename.split('.')[-1]}"
                upload_result = supabase.storage.from_("event-foto").upload(filename, content, {
                    "content-type": foto.content_type
                })

                if hasattr(upload_result, 'error') and upload_result.error:
                    raise HTTPException(status_code=500, detail=f"Upload foto baru gagal: {upload_result.error.message}")

                new_foto_url = supabase.storage.from_("event-foto").get_public_url(filename)

                # Hapus foto lama jika ada
                if existing_event["foto_url"] and existing_event["foto_url"] != new_foto_url:
                    try:
                        old_filename = existing_event["foto_url"].split('/')[-1]
                        supabase.storage.from_("event-foto").remove([old_filename])
                    except Exception as e:
                        print(f"Peringatan: Gagal menghapus foto lama '{old_filename}': {e}")

            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Terjadi kesalahan saat memproses foto: {str(e)}")
        event_update_data = {}

        if can_edit_all:
            event_update_data = {
                "judul": data.judul,
                "deskripsi": data.deskripsi,
                "tanggal_event": data.tanggal_event.isoformat(),
                "jam_mulai": data.jam_mulai.isoformat(),
                "durasi_event": data.durasi_event,
                "jumlah_tiket": data.jumlah_tiket,
                "tipe_tiket": data.tipe_tiket,
                "lokasi": data.lokasi,
                "latitude": data.latitude,
                "longitude": data.longitude,
                "foto_url": new_foto_url,
                "harga_tiket": float(data.harga_tiket) if data.harga_tiket is not None else 0.0
            }
            return {"message": "Anda berhasil mengedit semuanya", "data": event_update_data}
        else:
            event_update_data = {
                "judul": data.judul,
                "deskripsi": data.deskripsi,
                "lokasi": data.lokasi,
                "latitude": data.latitude,
                "longitude": data.longitude,
                "foto_url": new_foto_url,
            }
            return {"message": "Mohon maaf anda hanya dapat merubah bagian judul, deskripsi, lokasi, latitude, dan longitude", "data": event_update_data}

        response_update = (
            supabase.table("event")
            .update(event_update_data)
            .eq("id", event_id)
            .eq("akun_id", akun["id"])  
            .execute()
        )

        if hasattr(response_update, 'error') and response_update.error:
            raise HTTPException(status_code=500, detail=f"Gagal memperbarui event di database: {response_update.error.message}")
        
        if not response_update.data:
            raise HTTPException(status_code=404, detail="Event tidak ditemukan atau Anda tidak memiliki izin untuk memperbarui.")

        return {"message": "Event berhasil diperbarui", "data": response_update.data[0]}

    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan server saat memperbarui event: {str(e)}")
