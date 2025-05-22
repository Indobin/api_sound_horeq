from .base import BaseModel, constr, Optional, date, time, Decimal


class CreateEventModel(BaseModel):
    judul: constr(min_length=3, max_length=100)
    deskripsi: constr(min_length=10, max_length=1000)
    tanggal_event: date
    jam_mulai: time
    durasi_event: int
    harga_tiket: Decimal
    jumlah_tiket: int
    tipe_tiket: int
    lokasi: constr(min_length=3, max_length=100)
    latitude: float
    longtitude: float

    # class Config:
    #     json_schema_extra = {
    #         "example": {
    #             "judul": "Event Sound Horeq",
    #             "deskripsi": "Event ini dibuat untuk menyatukan komunitas sound system.",
    #             "tanggal_event": "2025-08-01",
    #             "jam_mulai": "18:00",
    #             "durasi_event": 3,
    #             "harga_tiket": 15000.0,
    #             "jumlah_tiket": 200,
    #             "status_tiket": True,
    #             "lokasi": "Alun-alun Jember",
    #             "latitude": -8.184486,
    #             "longtitude": 113.668075
    #         }
    #     }
