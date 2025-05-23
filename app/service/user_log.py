from datetime import datetime
import os
import json
from typing import List
from schemas.user_log import LogResponse
from file_read_backwards import FileReadBackwards
from pydantic import BaseModel, Field
USER_LOG_DIR = "user_log"


def insert_user_log(user_id: str, activity_type: str, status: str):
    os.makedirs(USER_LOG_DIR, exist_ok=True)
    log_file = os.path.join(USER_LOG_DIR, f"{user_id}_user_log.json")

    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": activity_type,
        "status": status
    }

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def get_user_logs(user_id: str, count: int) -> List[LogResponse]:
    log_file = os.path.join(USER_LOG_DIR, f"{user_id}_user_log.json")
    if not os.path.exists(log_file):
        print("No such file or directory")
        return []

    logs = []
    with FileReadBackwards(log_file, encoding="utf-8") as frb:
        for line in frb:
            try:
                log = json.loads(line)
                logs.append(LogResponse(**log))
                if len(logs) >= count:
                    break
            except json.JSONDecodeError:
                continue

    return logs