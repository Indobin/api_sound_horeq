from fastapi import HTTPException, UploadFile, File
from models.akun_models import RegisterModel, LoginModel, UpdateAkuntModel
from models.event_models import CreateEventModel
from models.forum_models import CreateForumModels
from app.supabase_client import supabase
from passlib.context import CryptContext
from jose import jwt
import os
from dotenv import load_dotenv
from datetime import datetime
