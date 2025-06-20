from .base import APIRouter, Depends, get_current_akun, TransaksiPayload, ScanQrPayload
from .base import transaksi, riwayat_tiket, scan_tiket_qr
router = APIRouter(prefix="/api/tiket", tags=["Tiket"])

@router.post("/transaksi/{event_id}/bayar")
async def bayar_event(
    event_id: int,
    payload: TransaksiPayload,
    akun: dict = Depends(get_current_akun)
):
    return await transaksi(event_id, payload, akun)

@router.get("/riwayat")
async def get_riwayat(
    akun: dict = Depends(get_current_akun)
):
    return await riwayat_tiket(akun)

@router.post("/scan-tiket")
async def scan_tiket(
    qr_code: ScanQrPayload,
    akun: dict = Depends(get_current_akun)
):
    return await scan_tiket_qr(qr_code, akun) 