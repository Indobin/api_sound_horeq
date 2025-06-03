from .base import APIRouter, Depends, get_current_akun
from .base import forum_chat, CreateForumModels, get_forum_chat

router = APIRouter(prefix="/api/forum-chat", tags=["Forum Chat"])

@router.post("/pesan")
async def create_forumChat(
 data: CreateForumModels,
 akun:dict = Depends(get_current_akun)
):
 return await forum_chat(data, akun)

@router.get("/pesan")
async def read_forumChat(
 akun:dict = Depends(get_current_akun)
):
 return await get_forum_chat(akun)