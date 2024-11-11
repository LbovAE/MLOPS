# Инструкция по запуску

### Предварительные требования
- Python 3.8+
- Установленные зависимости (pip install -r requirements.txt)

### Команды для запуска
1. Запуск MinIO для хранения данных:
        sh init_minio.sh
    

2. Запуск API сервиса:
        python3 service_handler.py
    

3. Работа с API:
    - Добавить модель:
                curl -X POST -H "Content-Type: application/json" -d '{"model_class":"Linear", "model_name":"logistic_regression", "hyperparameters":{}}' http://127.0.0.1:8000/model/create
        
    - Удалить модель:
                curl -X POST -H "Content-Type: application/json" -d '{"model_class":"Linear", "model_name":"logistic_regression"}' http://127.0.0.1:8000/model/remove
        
    - Обучить модель:
                curl -X POST -H "Content-Type: application/json" -d '{"model_class":"Linear", "model_name":"logistic_regression", "data":{"feature_1":[1.2, 0, 4], "feature_2":[3.4, 1, 4.7], "target":[0, 1, 0]}}' http://127.0.0.1:8000/model/train
        
    - Сделать предсказание:
                curl -X POST -H "Content-Type: application/json" -d '{"model_class":"Linear", "model_name":"logistic_regression", "data":{"feature_1":[1.2, 0, 4], "feature_2":[3.4, 1, 4.7]}}' http://127.0.0.1:8000/model/predict
        

### Дополнительные возможности
- Поддержка базовой аутентификации (если включена).