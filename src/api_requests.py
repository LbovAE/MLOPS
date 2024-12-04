
from pydantic import BaseModel

class AddModelRequest(BaseModel):
    model_class: str
    model_name: str
    hyperparameters: dict

class RemoveModelRequest(BaseModel):
    model_class: str
    model_name: str

class TrainRequest(BaseModel):
    model_class: str
    model_name: str
    data: dict

class PredictRequest(BaseModel):
    model_class: str
    model_name: str
    data: dict
