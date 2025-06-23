from .base import HTTPException, supabase, load_dotenv, os, TransaksiPayload, ScanQrPayload
import base64, requests
from datetime import datetime
from uuid import uuid4
load_dotenv()
MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY")

async def transaksi(event_id: int, payload: TransaksiPayload, akun: dict):
    if akun.get("role_akun_id") != 2:
        raise HTTPException(status_code=403, detail="Hanya peserta yang dapat membeli tiket.")

    qty = payload.qty
    if qty <= 0:
        raise HTTPException(status_code=400, detail="Qty tidak valid")

    event_data = (
        supabase
        .table("event")
        .select("id, judul, harga_tiket, jumlah_tiket, tipe_tiket")
        .eq("id", event_id)
        .is_("deleted_at", None)
        .execute()
    ).data

    if not event_data:
        raise HTTPException(status_code=404, detail="Event tidak ditemukan")
    if event_data[0]["tipe_tiket"] == 1:
        raise HTTPException(status_code=400, detail="Tiket gratis, tidak perlu ada pembayaran")
    
    event = event_data[0]

    # Cek ketersediaan tiket
    if event["jumlah_tiket"] is None or event["jumlah_tiket"] < qty:
        raise HTTPException(status_code=400, detail="Jumlah tiket tidak mencukupi")

    harga_total = event["harga_tiket"] * qty
    order_id = f"ORDER-{event_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Midtrans - Snap Token
    auth = base64.b64encode(f"{MIDTRANS_SERVER_KEY}:".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }

    midtrans_payload = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": harga_total
        },
        "item_details": [{
            "id": str(event_id),
            "price": event["harga_tiket"],
            "quantity": qty,
            "name": event["judul"]
        }],
        "customer_details": {
            "first_name": akun.get("nama", "Peserta"),
            "email": akun.get("email", "peserta@example.com")
        }
    }

    r = requests.post(
        "https://app.sandbox.midtrans.com/snap/v1/transactions",
        headers=headers,
        json=midtrans_payload
    )

    if not r.ok or "token" not in r.json():
        print(r.text)
        raise HTTPException(status_code=r.status_code, detail="Gagal membuat transaksi")

    res = r.json()

    trx = supabase.table("transaksi").insert({
        "order_id": order_id,
        "akun_id": akun["id"],
        "event_id": event_id,
        "qty": qty,
        "harga_total": harga_total,
        "status": "berhasil"
    }).execute().data[0]

   
    supabase.table("event").update({
        "jumlah_tiket": event["jumlah_tiket"] - qty
    }).eq("id", event_id).execute()

    
    tiket_qr = []
    for _ in range(qty):
        tiket_qr.append({
            "transaksi_id": trx["id"],
            "qr_code": str(uuid4()),
            "status": "unused"
        })
    supabase.table("tiket_terbit").insert(tiket_qr).execute()

    return {
        "snap_token": res["token"],
        "redirect_url": res["redirect_url"],
        "order_id": order_id,
        "harga_total": harga_total,
        "event": {
            "judul": event["judul"],
            "qty": qty
        },
        "tiket_qr": tiket_qr
    }

async def transaksi_gratis(event_id: int, payload: TransaksiPayload, akun: dict):
    if akun.get("role_akun_id") != 2:
        raise HTTPException(status_code=403, detail="Hanya peserta yang dapat membeli tiket.")

    qty = payload.qty
    if qty <= 0:
        raise HTTPException(status_code=400, detail="Qty tidak valid")

    event_data = (
        supabase
        .table("event")
        .select("id, judul, harga_tiket, jumlah_tiket, tipe_tiket")
        .eq("id", event_id)
        .is_("deleted_at", None)
        .execute()
    ).data

    if not event_data:
        raise HTTPException(status_code=404, detail="Event tidak ditemukan")
    if event_data[0]["tipe_tiket"] == 2:
        raise HTTPException(status_code=400, detail="Tiket berbayar, harus ada pembayaran")
    event = event_data[0]

    # Cek ketersediaan tiket
    if event["jumlah_tiket"] is None or event["jumlah_tiket"] < qty:
        raise HTTPException(status_code=400, detail="Jumlah tiket tidak mencukupi")
    
    harga_total = event["harga_tiket"] * qty
    order_id = f"ORDER-{event_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    trx = supabase.table("transaksi").insert({
        "order_id": order_id,
        "akun_id": akun["id"],
        "event_id": event_id,
        "qty": qty,
        "harga_total": harga_total,
        "status": "berhasil"
    }).execute().data[0]

    supabase.table("event").update({
        "jumlah_tiket": event["jumlah_tiket"] - qty
    }).eq("id", event_id).execute()

    tiket_qr = []
    for _ in range(qty):
        tiket_qr.append({
            "transaksi_id": trx["id"],
            "qr_code": str(uuid4()),
            "status": "unused"
        })
    supabase.table("tiket_terbit").insert(tiket_qr).execute()

    return {
        "order_id": order_id,
        "harga_total": harga_total,
        "event": {
            "judul": event["judul"],
            "qty": qty
        },
        "tiket_qr": tiket_qr
    }
async def riwayat_tiket(akun: dict):
    if akun.get("role_akun_id") != 2:
        raise HTTPException(status_code=403, detail="Hanya peserta yang dapat melihat riwayat tiket.")
    try:
        response = (
            supabase
            .table("tiket_terbit")
            .select("qr_code, status, transaksi(event(id,judul, tanggal_event, jam_mulai, lokasi))")
            .eq("transaksi.akun_id", akun["id"])
            .execute()
        )

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def scan_tiket_qr(payload: ScanQrPayload, akun: dict):
    qr_code = payload.qr_code
    if akun.get("role_akun_id") != 1:
        raise HTTPException(status_code=403, detail="Hanya penyelenggara yang dapat menscan tiket.")

    tiket_data = (
        supabase
        .table("tiket_terbit")
        .select("id, status, transaksi(event(akun_id))")
        .eq("qr_code", qr_code)
        .limit(1)
        .execute()
    ).data

    if not tiket_data:
        raise HTTPException(status_code=404, detail="Tiket tidak ditemukan")

    tiket = tiket_data[0]
    penyelenggara_id = tiket.get("transaksi", {}).get("event", {}).get("akun_id")

    if penyelenggara_id != akun["id"]:
        raise HTTPException(status_code=403, detail="Anda tidak berhak menscan tiket ini!")

    if tiket["status"] == "used":
        raise HTTPException(status_code=400, detail="Tiket sudah digunakan")

    supabase.table("tiket_terbit").update({"status": "used"}).eq("id", tiket["id"]).execute()

    return {"message": "Tiket valid dan berhasil digunakan"}

