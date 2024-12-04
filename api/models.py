
import pandas as pd
from sklearn.linear_model import LogisticRegression
from catboost import CatBoostClassifier
from typing import Literal
from utils import push_file_to_dvc
import pickle
import boto3

class S3Config:
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name, model_key):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.bucket = bucket_name
        self.key = model_key

class Models:
    def __init__(self, s3_config: S3Config):
        self.s3_client = s3_config.s3_client
        self.bucket = s3_config.bucket
        self.key = s3_config.key
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=self.key)
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
        pickle_data = pickle.dumps(self.models)
        self.s3_client.put_object(Body=pickle_data, Bucket=self.bucket, Key=self.key)

    def delete_model(self, model_class: str, model_name: str):
        del self.models[model_class]["models"][model_name]
        pickle_data = pickle.dumps(self.models)
        self.s3_client.put_object(Body=pickle_data, Bucket=self.bucket, Key=self.key)

    def prepare_data(self, data: dict, train: bool = True):
        df = pd.DataFrame(data)
        if train:
            data_train, target_train = df.iloc[:, :-1], df.iloc[:, -1]
            return data_train, target_train
        return df

    def train(self, model_class: Literal["Linear models", "Tree models"], model_name: str, data: dict, data_name: str):
        data_train, target_train = self.prepare_data(data)
        clf = self.models[model_class]["models"][model_name]
        clf["model"].fit(data_train, target_train)
        clf["is_trained"] = True
        pickle_data = pickle.dumps(self.models)
        self.s3_client.put_object(Body=pickle_data, Bucket=self.bucket, Key=self.key)
        push_file_to_dvc(data, data_name)

    def predict(self, model_class: Literal["Linear models", "Tree models"], model_name: str, data: dict, data_name: str):
        data_test = self.prepare_data(data, train=False)
        clf = self.models[model_class]["models"][model_name]
        pred = list(clf["model"].predict(data_test))
        push_file_to_dvc(data, data_name)
        return pred

    def get_available_models(self):
        return {
            "Семейство Linear models": {
                "Модели": [*self.models["Linear models"]["models"].keys()]
            },
            "Семейство Tree models": {
                "Модели": [*self.models["Tree models"]["models"].keys()]
            },
        }
