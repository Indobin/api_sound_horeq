from .base import BaseModel,  constr, Optional, datetime, date, time

class EventModel(BaseModel):
    id: int
    judul: constr(min_length=3, max_length=100)
    deskripsi: constr(min_length=10, max_length=1000)
    tanggal_event: date
    durasi_event: int
    jam_mulai: time
    harga_tiket: numeric
    jumlah_tiket: int
    status_tiket: bool
    lokasi : constr(min_length=3, max_length=100)
