import pandas as pd
from sklearn.linear_model import LogisticRegression
from catboost import CatBoostClassifier
from typing import Literal
from utils import push_file_to_dvc
import pickle
import boto3

s3_client = boto3.client('s3',
                        endpoint_url='http://127.0.0.1:9000',
                        aws_access_key_id='obai9Szm6zF7XpWr6UTQ',
                        aws_secret_access_key='vNZBQjoCigmI6QDhMIG2BQhm6Vgx4WFGqQkhAdZ4')

key = "models.pkl"
bucket = "models"


class Models:
    def __init__(self):
        try:
            response = s3_client.get_object(Bucket=bucket, Key=key)
            pickle_data = response['Body'].read()
            self.models = pickle.loads(pickle_data)
        except:
            self.models = {
            "Linear models": {"models": {}},
            "Tree models": {"models": {}}
        }

    def add_model(
        self,
        model_class: Literal["Linear models", "Tree models"],
        model_name: str,
        hyperparameters: dict = {},
    ):
        """
        Добавляет новую модель в класс

        Аргументы:
        - model_class (Literal["Linear models", "Tree models"]): Семейство
        моделей - "Linear models" или "Tree models"
        - model_name (str): Название модели
        - hyperparameters (dict, опционально): Гиперпараметры модели.
        По умолчанию - пустой словарь

        """

        if model_class == "Linear models":
            self.models[model_class]["models"] = {
                model_name: {
                    "model": LogisticRegression(**hyperparameters),
                    "is_trained": False,
                }
            }
        else:
            self.models[model_class]["models"] = {
                model_name: {
                    "model": CatBoostClassifier(**hyperparameters),
                    "is_trained": False,
                }
            }
        # save model config
        pickle_data = pickle.dumps(self.models)
        s3_client.put_object(Body=pickle_data, Bucket=bucket, Key=key)

    def delete_model(self, model_class: str, model_name: str):
        """
        Удаляет модель из класса

        Аргументы:
        - model_class (str): Семейство моделей, из которого нужно удалить
        модель
        - model_name (str): Название модели, которую нужно удалить

        """

        del self.models[model_class]["models"][model_name]
        # save model config
        pickle_data = pickle.dumps(self.models)
        s3_client.put_object(Body=pickle_data, Bucket=bucket, Key=key)

    def prepare_data(self, data: dict, train: bool = True):
        """
        Подготавливает данные для обучения модели или для предсказания

        Аргументы:
        - data (dict): Словарь с данными, содержащий признаки и целевую
        переменную
        - train (bool, опционально): Флаг, указывающий, являются ли данные для
        обучения модели или для предсказания. По умолчанию - True,
        то есть данные предназначены для обучения модели

        Возвращает:
        Если train=True:
        - tuple: Кортеж из двух элементов: X_train - матрица признаков для
        обучения, y_train - вектор с целевой переменной.
        Если train=False:
        - pd.DataFrame: DataFrame с данными, готовыми для предсказания

        """

        df = pd.DataFrame(data)
        if train:
            data_train, target_train = df.iloc[:, :-1], df.iloc[:, -1]
            return data_train, target_train
        return df

    def train(
        self,
        model_class: Literal["Linear models", "Tree models"],
        model_name: str,
        data: dict,
        data_name: str
    ):
        """
        Обучает указанную модель на предоставленных данных

        Аргументы:
        - model_class (Literal["Linear models", "Tree models"]): Класс модели,
        которую нужно обучить - "Linear models" или "Tree models"
        - model_name (str): Название модели, которую нужно обучить
        - data (dict): Словарь с данными для обучения, содержащий признаки и
        целевую переменную
        - data_name (str): Название датасета
        
        """

        data_train, target_train = self.prepare_data(data)
        clf = self.models[model_class]["models"][model_name]
        clf["model"].fit(data_train, target_train)
        clf["is_trained"] = True
        # save model config
        pickle_data = pickle.dumps(self.models)
        s3_client.put_object(Body=pickle_data, Bucket=bucket, Key=key) 
        # save data
        push_file_to_dvc(data, data_name)

    def predict(
        self,
        model_class: Literal["Linear models", "Tree models"],
        model_name: str,
        data: dict,
        data_name: str
    ):
        """
        Выполняет предсказание с использованием указанной модели на
        предоставленных данных

        Аргументы:
        - model_class (Literal["Linear models", "Tree models"]): Класс модели,
        для которой нужно выполнить предсказание - "Linear models" или
        "Tree models"
        - model_name (str): Название модели, для которой нужно выполнить
        предсказание
        - data (dict): Словарь с данными для предсказания, содержащий признаки
        - data_name (str): Название датасета

        Возвращает:
        - list: Список предсказанных значений

        """

        data_test = self.prepare_data(data, train=False)
        clf = self.models[model_class]["models"][model_name]
        pred = list(clf["model"].predict(data_test))
        push_file_to_dvc(data, data_name)
        return pred

    def get_available_models(self):
        """
        Возвращает доступные модели, разделенные на семейства
        Linear models" и "Tree models"

        Возвращает:
        - dict: Словарь с доступными моделями, разделенными на семейства:
            - "Семейство Linear models":
                - "Модели": Список названий моделей в семействе Linear models
            - "Семейство Tree models":
                - "Модели": Список названий моделей в семействе Tree models
        """

        return {
            "Семейство Linear models": {
                "Модели": [*self.models["Linear models"]["models"].keys()]
            },
            "Семейство Tree models": {
                "Модели": [*self.models["Tree models"]["models"].keys()]
            },
        }
