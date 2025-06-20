from fastapi import APIRouter, Depends,  FastAPI, UploadFile, File, Form
from models.akun_models import RegisterModel, LoginModel, UpdateAkuntModel
from controllers.auth_controller import register_akun, login_akun, edit_profile, edit_foto
from models.event_models import CreateEventModel
from models.forum_models import CreateForumModels
from models.tiket_models import TransaksiPayload
from controllers.event_controller import create_event, event_penyelenggara
from controllers.event_controller import event_peserta, eventId_peserta
from controllers.forum_controller import forum_chat, get_forum_chat
from controllers.tiket_controller import transaksi, riwayat_tiket, scan_tiket_qr
from app.auth import get_current_akun
from typing import Optional