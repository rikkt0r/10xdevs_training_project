from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class DataResponse[DataType](BaseModel):
    data: DataType


class PaginationSerializer(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int


class PaginatedDataResponse[DataType](BaseModel):
    data: DataType
    pagination: PaginationSerializer


class DataWithMessageResponse[DataType](BaseModel):
    data: DataType
    message: str
