from .base import BaseModel, constr, Optional, condecimal
from datetime import datetime

class CreateTransaksiModel(BaseModel):
    akun_id: int
    event_id: int
    qty: int
    harga_total: condecimal(ge=0)
    status: constr(min_length=3, max_length=100)
    order_id: Optional[constr(min_length=3, max_length=100)] = None
    created_at: Optional[datetime] = None