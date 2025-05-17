from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

async def custom_validation(request: Request, exc: RequestValidationError):
    translated_errors = []
    for error in exc.errors():
        field = error["loc"][-1]
        msg = error["msg"]

        if "valid email" in msg:
            msg = "Format email tidak valid"
        elif "at least" in msg:
            msg = f"Panjang minimal {error['ctx']['min_length']} karakter"
        elif "too short" in msg:
            msg = "Teks terlalu pendek"
        elif "too long" in msg:
            msg = "Teks terlalu panjang"
        elif "value is not a valid enumeration" in msg:
            msg = "Nilai tidak termasuk pilihan yang tersedia"

        translated_errors.append({
            "field": field,
            "message": msg
        })

    return JSONResponse(
        status_code=422,
        content={"detail": translated_errors}
    )
