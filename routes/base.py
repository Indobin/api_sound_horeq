from fastapi import APIRouter, Depends,  FastAPI, UploadFile, File, Form
from models.akun_models import RegisterModel, LoginModel, UpdateAkuntModel
from controllers.auth_controller import register_akun, login_akun, edit_profile
from models.event_models import CreateEventModel
from controllers.event_controller import create_event, event_penyelenggara
from controllers.event_controller import event_peserta, eventId_peserta
from app.auth import get_current_akun