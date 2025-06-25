from .base import HTTPException, supabase, datetime, Query
from .base import CreateEventModel, UploadFile, Form, Decimal, date, File
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
            .select("*")
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
            .select("*")
            .eq("akun_id", akun["id"])
            .is_("deleted_at", None)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
async def eventId_penyelenggara(event_id: int, akun: dict):
    if akun.get("role_akun_id") != 1:
        raise HTTPException(status_code=403, detail="Hanya penyelenggara yang dapat mengakses data ini.")
    try:
        # Ambil data event
        event = (
            supabase
            .table("event")
            .select("*")
            .eq("id", event_id)
            .is_("deleted_at", None)
            .single()
            .execute()
        )
        if not event.data:
            raise HTTPException(status_code=404, detail="Event tidak ditemukan")

        # Cek apakah event ini punya transaksi
        transaksi = supabase.table("transaksi").select("id").eq("event_id", event_id).limit(1).execute()
        ada_transaksi = bool(transaksi.data)

        return {
            "event": event.data,
            "ada_transaksi": ada_transaksi
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
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

async def lokasi_event(akun: dict):
    if akun.get("role_akun_id") != 2:
        raise HTTPException(status_code=403, detail="Hanya peserta yang dapat mengakses data ini.")

    try:
        response = (
            supabase
            .table("event")
            .select("lokasi, longitude, latitude")
            .is_("deleted_at", None)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_event(id: int, akun: dict, 
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
                       foto: Optional[UploadFile] = File(None)):
    try:
        if akun.get("role_akun_id") != 1:
            raise HTTPException(status_code=403, detail="Hanya penyelenggara yang dapat mengedit event")

        # Ambil data event
        existing = supabase.table("event").select("*").eq("id", id).single().execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Event tidak ditemukan")

        # Cek apakah ada transaksi
        transaksi = supabase.table("transaksi").select("id").eq("event_id", id).limit(1).execute()
        ada_transaksi = bool(transaksi.data)

        update_data = {}

        # Validasi dan pemrosesan setiap field
        if judul: update_data["judul"] = judul
        if deskripsi: update_data["deskripsi"] = deskripsi
        if tanggal_event:
            if tanggal_event < datetime.now().date():
                raise HTTPException(status_code=400, detail="Tanggal event tidak boleh di masa lalu")
            update_data["tanggal_event"] = tanggal_event.isoformat()
        if jam_mulai:
            jam_obj = datetime.strptime(jam_mulai, "%H:%M:%S").time()
            update_data["jam_mulai"] = jam_obj.isoformat()
        if durasi_event is not None:
            update_data["durasi_event"] = durasi_event

        # Field tidak bisa diubah jika sudah ada transaksi
        if not ada_transaksi:
            if harga_tiket is not None:
                harga_decimal = Decimal(harga_tiket)
                if harga_decimal < 0:
                    raise HTTPException(status_code=400, detail="Harga tiket tidak boleh negatif")
                update_data["harga_tiket"] = float(harga_decimal)
            if jumlah_tiket is not None:
                update_data["jumlah_tiket"] = jumlah_tiket
            if tipe_tiket is not None:
                update_data["tipe_tiket"] = tipe_tiket

        if lokasi: update_data["lokasi"] = lokasi
        if latitude is not None: update_data["latitude"] = latitude
        if longitude is not None: update_data["longitude"] = longitude

        # Proses upload foto jika ada
        if foto:
            content = await foto.read()
            if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Ukuran foto maksimal 1MB")

            filename = f"{akun['id']}_{int(datetime.utcnow().timestamp())}.{foto.filename.split('.')[-1]}"
            upload_result = supabase.storage.from_("event-foto").upload(filename, content, {
                "content-type": foto.content_type
            })

            if hasattr(upload_result, 'error') and upload_result.error:
                raise HTTPException(status_code=500, detail="Upload foto gagal")

            public_url = supabase.storage.from_("event-foto").get_public_url(filename)
            update_data["foto_url"] = public_url

        if not update_data:
            raise HTTPException(status_code=400, detail="Tidak ada data yang dikirim untuk diperbarui")

        # Update ke DB
        response = supabase.table("event").update(update_data).eq("id", id).execute()
        return {"message": "Event berhasil diperbarui", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

async def delete_event(event_id: int, akun: dict):
    if akun.get("role_akun_id") != 1:
        raise HTTPException(status_code=403, detail="Hanya penyelenggara yang dapat menghapus event.")

    try:
        event = (
            supabase
            .table("event")
            .select("id, akun_id")
            .eq("id", event_id)
            .is_("deleted_at", None)
            .single()
            .execute()
        )

        if not event.data:
            raise HTTPException(status_code=404, detail="Event tidak ditemukan atau sudah dihapus.")

        if event.data["akun_id"] != akun["id"]:
            raise HTTPException(status_code=403, detail="Anda tidak memiliki izin untuk menghapus event ini.")
        transaki = supabase.table("transaksi").select("id").eq("event_id", event_id).limit(1).execute()
        if transaki.data:
            raise HTTPException(status_code=400, detail="Event ini sudah memiliki transaksi, tidak dapat dihapus.")
        deleted_at = datetime.utcnow().isoformat()

        supabase \
            .table("event") \
            .update({"deleted_at": deleted_at}) \
            .eq("id", event_id) \
            .execute()

        return {"message": "Event berhasil dihapus."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus event: {str(e)}")

async def event_detail_penyelenggara(event_id: int, akun: dict):
    # Validasi role penyelenggara
    if akun.get("role_akun_id") != 1:
        raise HTTPException(status_code=403, detail="Hanya penyelenggara yang dapat mengakses data ini.")

    try:
        # Ambil data event
        event_query = (
            supabase
            .table("event")
            .select(
                "judul, deskripsi, tanggal_event, jam_mulai, lokasi, jumlah_tiket, "
                "harga_tiket, durasi_event, foto_url, tipe_tiket, akun_id"
            )
            .eq("id", event_id)
            .is_("deleted_at", None)
            .single()
            .execute()
        )

        event_data = event_query.data

        if not event_data:
            raise HTTPException(status_code=404, detail="Event tidak ditemukan.")

        # Cek apakah event milik akun penyelenggara ini
        if event_data["akun_id"] != akun["id"]:
            raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke event ini.")

        # Ambil transaksi yang berhasil
        transaksi_query = (
            supabase
            .table("transaksi")
            .select("qty, harga_total")
            .eq("event_id", event_id)
            .eq("status", "berhasil")
            .execute()
        )

        transaksi_data = transaksi_query.data or []

        total_tiket_terjual = sum(row["qty"] for row in transaksi_data)
        total_pendapatan = sum(float(row["harga_total"]) for row in transaksi_data)

        # Siapkan data respon tanpa akun_id
        response_data = {
            "judul": event_data["judul"],
            "deskripsi": event_data["deskripsi"],
            "foto_url": event_data["foto_url"],
            "durasi_event": event_data["durasi_event"],
            "harga_tiket": event_data["harga_tiket"],
            "tipe_tiket": event_data["tipe_tiket"],
            "tanggal_event": event_data["tanggal_event"],
            "jam_mulai": event_data["jam_mulai"],
            "lokasi": event_data["lokasi"],
            "jumlah_tiket": event_data["jumlah_tiket"],
            "total_tiket_terjual": total_tiket_terjual,
            "total_pendapatan": total_pendapatan
        }

        return {"data": response_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil detail event: {str(e)}")