from .base import HTTPException, supabase, datetime
from .base import CreateEventModel, UploadFile

MAX_FILE_SIZE_MB = 1

# ================= PESERTA ====================
async def event_peserta(akun: dict):
    if akun.get("role_akun_id") != 2:
        raise HTTPException(status_code=403, detail="Hanya peserta yang dapat mengakses data ini.")

    try:
        response = (
            supabase
            .table("event")
            .select("id, judul, tanggal_event, jam_mulai, lokasi, harga_tiket")
            .is_("deleted_at", None)
            .order("created_at", desc=True)
            .execute()
        )
        return {"data": response.data}
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


# ================ PENYELENGGARA =================
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


async def create_event(akun: dict, data: CreateEventModel, foto: UploadFile):
    try:
        if akun.get("role_akun_id") != 1:
            raise HTTPException(status_code=403, detail="Hanya penyelenggara yang dapat membuat event")

        created = datetime.utcnow()

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

        # Simpan ke tabel event
        event_data = {
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
            "foto_url": public_url,
            "akun_id": akun["id"],
            "created_at": created.isoformat(),
            "harga_tiket": float(data.harga_tiket) if data.harga_tiket is not None else 0.0
        }

        response = supabase.table("event").insert(event_data).execute()

        return {"message": "Event berhasil dibuat", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# ================ DELETE EVENT =================
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
    if akun.get("role_akun_id") != 1:
        raise HTTPException(status_code=403, detail="Hanya penyelenggara yang dapat mengakses data ini.")

    try:
        # Ambil detail event
        event_response = (
            supabase
            .table("event")
            .select("id, tanggal_event, jam_mulai, lokasi, jumlah_tiket, akun_id")
            .eq("id", event_id)
            .is_("deleted_at", None)
            .single()
            .execute()
        )

        if not event_response.data:
            raise HTTPException(status_code=404, detail="Event tidak ditemukan.")

        if event_response.data["akun_id"] != akun["id"]:
            raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke event ini.")

        event_data = event_response.data

        # Ambil data transaksi yang berhasil
        transaksi_response = (
            supabase
            .table("transaksi")
            .select("qty, harga_total")
            .eq("event_id", event_id)
            .eq("status", "dibayar")  # sesuaikan dengan status sukses di sistemmu
            .execute()
        )

        transaksi_data = transaksi_response.data or []

        total_tiket_terjual = sum([row["qty"] for row in transaksi_data])
        total_pendapatan = sum([float(row["harga_total"]) for row in transaksi_data])

        # Gabungkan semua data
        return {
            "data": {
                "tanggal_event": event_data["tanggal_event"],
                "jam_mulai": event_data["jam_mulai"],
                "lokasi": event_data["lokasi"],
                "jumlah_tiket": event_data["jumlah_tiket"],
                "total_tiket_terjual": total_tiket_terjual,
                "total_pendapatan": total_pendapatan
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil detail event: {str(e)}")
