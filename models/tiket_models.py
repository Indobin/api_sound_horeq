from pydantic import BaseModel, Field

class TransaksiPayload(BaseModel):
    qty: int = Field(..., gt=0, description="Jumlah tiket yang dibeli, harus lebih dari 0")
