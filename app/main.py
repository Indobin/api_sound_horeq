from fastapi import FastAPI
from routes import auth_route, event_route, forum_route, tiket_route
from fastapi.exceptions import RequestValidationError
from exceptions.validation_handler import custom_validation
app = FastAPI()

app.include_router(auth_route.router)
app.include_router(event_route.router)
app.include_router(forum_route.router)
app.include_router(tiket_route.router)
app.add_exception_handler(RequestValidationError, custom_validation)
@app.get("/")
def read_root():
    
    return {"message": "Hello World"}