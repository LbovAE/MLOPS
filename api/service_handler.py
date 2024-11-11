from fastapi import FastAPI, HTTPException, Depends
from src.model_manager import ModelManager
import uvicorn
from src.api_requests import (
    AddModelRequest,
    RemoveModelRequest,
    TrainRequest,
    PredictRequest,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from log_config import get_logger

app = FastAPI()
manager = ModelManager()
logger = get_logger(name)

security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "admin123")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.get("/model_classes")
def list_model_classes(credentials: HTTPBasicCredentials = Depends(authenticate)):
    logger.info("Получение списка доступных классов моделей.")
    return manager.get_model_classes()

@app.post("/model/create")
def create_model(request: AddModelRequest, credentials: HTTPBasicCredentials = Depends(authenticate)):
    logger.info(f"Добавление новой модели: {request.model_class}, {request.model_name}.")
    try:
        manager.create_model(request.model_class, request.model_name, request.hyperparameters)
    except ValueError:
        logger.error("Ошибка добавления модели. Неверный класс модели.")
        raise HTTPException(status_code=400, detail="Неверный класс модели. Выберите правильный.")
    logger.info("Модель успешно добавлена.")
    return {"message": "Модель успешно добавлена."}

@app.post("/model/remove")
def remove_model(request: RemoveModelRequest, credentials: HTTPBasicCredentials = Depends(authenticate)):
    logger.info(f"Удаление модели: {request.model_class}, {request.model_name}.")
    try:
        manager.delete_model(request.model_class, request.model_name)
    except KeyError:
        logger.error("Ошибка удаления модели: модель не найдена.")
        raise HTTPException(status_code=404, detail="Модель не найдена.")
    logger.info("Модель успешно удалена.")
    return {"message": "Модель успешно удалена."}

@app.post("/model/train")
def train_model(request: TrainRequest, credentials: HTTPBasicCredentials = Depends(authenticate)):
    logger.info(f"Обучение модели: {request.model_class}, {request.model_name}.")
    if not isinstance(request.data, dict):
        raise HTTPException(status_code=400, detail="Данные должны быть в формате словаря.")
    
    if len(request.data) < 2:
        raise HTTPException(status_code=400, detail="Недостаточно данных.")
    
    try:
        manager.train_model(request.model_class, request.model_name, request.data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    logger.info("Модель успешно обучена.")
    return {"message": "Модель успешно обучена."}

@app.post("/model/predict")
def predict(request: PredictRequest, credentials: HTTPBasicCredentials = Depends(authenticate)):
    logger.info(f"Предсказание для модели: {request.model_class}, {request.model_name}.")
    if not isinstance(request.data, dict):
        raise HTTPException(status_code=400, detail="Данные должны быть в формате словаря.")

    try:
        prediction = manager.make_prediction(request.model_class, request.model_name, request.data)
    except KeyError:
        logger.error("Ошибка предсказания: модель не найдена.")
        raise HTTPException(status_code=404, detail="Модель не найдена.")
    except Exception as e:
        logger.error(f"Ошибка предсказания: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    logger.info("Предсказание успешно выполнено.")
    return {"prediction": prediction}

if name == "main":
    uvicorn.run(app, host="127.0.0.1", port=8000)