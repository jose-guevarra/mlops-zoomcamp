#!/usr/bin/env python
# coding: utf-8

import sys

import pickle
import pandas as pd
from flask import Flask, request, jsonify

categorical = ['PULocationID', 'DOLocationID']

def read_data(year, month):
    file_url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    df = pd.read_parquet(file_url)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    return df


def predict(df):

    with open('model.bin', 'rb') as f_in:
        dv, model = pickle.load(f_in)

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)

    print("MEAN DURATION",  y_pred.mean())

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['prediction_duration'] = y_pred

    return df_result, y_pred.mean()


def run(year, month):
    df = read_data(year, month)
    df_result = predict(df)

    output_file = 'df_result.parquet'
    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )

app = Flask('duration-prediction')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    resp = request.get_json()

    df = read_data(resp['year'], resp['month'])
    df_result, pred_mean = predict(df)

    result = {
        'pred_mean': pred_mean
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9696)