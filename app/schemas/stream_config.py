from pydantic import BaseModel


class StreamUrlRequest(BaseModel):
    stream_url: str

    class Config:
        orm_mode = True
