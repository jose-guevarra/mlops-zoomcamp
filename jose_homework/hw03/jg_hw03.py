import os
from pathlib import Path
import httpx

import mlflow.sklearn
import pandas as pd
from prefect import flow, task
import pickle

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error

import mlflow


mlflow.set_tracking_uri("http://0.0.0.0:7003")
mlflow.set_experiment("jg-hw03")

models_folder = Path('models')
models_folder.mkdir(exist_ok=True)


DATA_FILE_NAME="yellow_tripdata_2023-03.parquet"
DATA_FILE_PATH=f'data/{DATA_FILE_NAME}'


categorical = ['PULocationID', 'DOLocationID']
numerical = ['trip_distance']


@task(retries=4, retry_delay_seconds=5, log_prints=True)
def fetch_data():
    data_url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{DATA_FILE_NAME}'
    resp = httpx.get(data_url)
    if resp.status_code >=400:
        raise Exception('Data download failed.')

    with open(DATA_FILE_PATH, 'wb') as f:
        f.write(resp.content)


@task(log_prints=True)
def read_dataframe(filename: str):
    df = pd.read_parquet(filename)
    print("SHAPE: ", df.shape)

    df['duration'] = df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    df[categorical] = df[categorical].astype(str)

    return df


@task(log_prints=True)
def train_model(df):
    train_dicts = df[categorical + numerical].to_dict(orient='records')

    dv = DictVectorizer()
    X_train = dv.fit_transform(train_dicts)
    print("X_TRAIN: ", X_train.shape)
    target = 'duration'
    y_train = df[target].values
    return X_train, y_train, dv


@task(log_prints=True)
def get_rmse(X_train, y_train):
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    print("INTERCEPT: ", lr.intercept_)

    y_pred = lr.predict(X_train)
    with mlflow.start_run() as run:
        rmse = root_mean_squared_error(y_train, y_pred)
        mlflow.log_metric("rmse", rmse)
        print("RMSE: ", rmse)
    return lr


@task(log_prints=True)
def register_model(model, dv):
    with mlflow.start_run() as run:

        with open("models/preprocessor.b", "wb") as f_out:
            pickle.dump(dv, f_out)
        mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")

        mlflow.sklearn.log_model(model, artifact_path="models_mlflow")


@flow()
def read_data(filename: str):
    return read_dataframe(filename)


@flow()
def download_data():
    fetch_data()


if __name__ == '__main__':

    download_data()
    df = read_data(DATA_FILE_PATH)
    print("PROCESSED SHAPE: ", df.shape)
    X_train, y_train, dv = train_model(df)
    lr = get_rmse(X_train, y_train)
    register_model(lr, dv)