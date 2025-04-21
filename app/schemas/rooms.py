from pydantic import BaseModel


class RoomsResponse(BaseModel):
    name: str
    status: str
    num: int

    class Config:
        orm_mode = True
