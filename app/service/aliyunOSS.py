# oss_client.py
import os
import oss2
from core.config import settings

# 替换为你的实际配置
auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)

ALLOWED_SUFFIX = {"jpg", "jpeg", "png", "gif"}


def upload_avatar(file_bytes: bytes, file_suffix: str) -> str:
    import uuid
    os.environ.pop('HTTP_PROXY', None)
    os.environ.pop('HTTPS_PROXY', None)
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)
    file_suffix = file_suffix.lower()
    if file_suffix not in ALLOWED_SUFFIX:
        raise ValueError("不支持的文件类型")

    filename = f"avatars/{uuid.uuid4().hex}.{file_suffix}"
    bucket.put_object(filename, file_bytes)
    return f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{filename}"
