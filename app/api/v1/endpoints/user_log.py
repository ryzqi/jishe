from fastapi import APIRouter, Depends
from core.security import get_current_user
from schemas import LogResponse
from models import User
from typing import List
from service.user_log import insert_user_log, get_user_logs
USER_LOG_DIR = "user_log"

router = APIRouter()


@router.get("/{count}", summary="获取近期用户日志")
async def get_user_log(
        count: int,
        user: User = Depends(get_current_user)
) -> List[LogResponse]:
    return get_user_logs(user.id, count)


