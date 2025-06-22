from .base import BaseModel, constr, Optional, date, time, condecimal


class CreateEventModel(BaseModel):
    judul: constr(min_length=3, max_length=100)
    deskripsi: constr(min_length=10, max_length=1000)
    tanggal_event: date
    jam_mulai: time
    durasi_event: int
    harga_tiket: Optional[condecimal(ge=0)] = None
    jumlah_tiket: int
    tipe_tiket: int
    lokasi: constr(min_length=3, max_length=100)
    latitude: float
    longitude: float

class UpdateEventModel(BaseModel):
    judul: Optional[constr(min_length=3, max_length=100)]
    deskripsi: Optional[constr(min_length=10, max_length=1000)]
    tanggal_event: Optional[date]
    jam_mulai: Optional[time]
    durasi_event: Optional[int]
    harga_tiket: Optional[condecimal(ge=0)] = None
    jumlah_tiket: Optional[int]
    tipe_tiket: Optional[int]
    lokasi: Optional[constr(min_length=3, max_length=100)]
    latitude: Optional[float]
    longitude: Optional[float]
