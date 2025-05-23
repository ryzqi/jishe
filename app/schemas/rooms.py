from pydantic import BaseModel


class RoomsResponse(BaseModel):
    name: str
    status: str
    num: int
    stock_id: int

    class Config:
        orm_mode = True
