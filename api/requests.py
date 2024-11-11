from pydantic import BaseModel
from typing import Union


class AddModelRequest(BaseModel):
    model_class: str
    model_name: str
    hyperparameters: Union[dict, None] = None


class DeleteModelRequest(BaseModel):
    model_class: str
    model_name: str


class TrainModelRequest(BaseModel):
    model_class: str
    model_name: str
    data: dict
    data_name: str


class PredictionModelRequest(BaseModel):
    model_class: str
    model_name: str
    data: dict
    data_name: str