import os
import pymysql
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

# 模型保存路径
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "unified_lstm_model.h5")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.npy")

# 数据库读取
def get_all_data():
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="nong",
        charset="utf8mb4"
    )
    cursor = db.cursor()
    cursor.execute("""
        SELECT data, variety, price
        FROM nongapp_productprice
        ORDER BY variety, data;
    """)
    data = cursor.fetchall()
    db.close()
    return pd.DataFrame(data, columns=["data", "variety", "price"])

# 数据清洗
def clean_data(df):
    df = df.dropna()
    df = df.drop_duplicates(subset=["data", "variety"])
    return df

# 数据预处理（按品种分别处理后合并）
def preprocess_all_varieties(df, sequence_length=7):
    all_X, all_y = [], []
    all_varieties = df["variety"].unique()
    scaler = MinMaxScaler()

    for variety in all_varieties:
        df_var = df[df["variety"] == variety].sort_values("data")
        if len(df_var) < sequence_length + 7:
            continue

        scaled_prices = scaler.fit_transform(df_var[["price"]])
        for i in range(len(scaled_prices) - sequence_length):
            X_seq = scaled_prices[i:i + sequence_length]
            y_val = scaled_prices[i + sequence_length]
            all_X.append(X_seq)
            all_y.append(y_val)

    X = np.array(all_X).reshape(-1, sequence_length, 1)
    y = np.array(all_y).reshape(-1, 1)
    return X, y, scaler

# 模型定义
def create_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(64, input_shape=input_shape))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model

# 模型训练
def train_unified_model():
    df = get_all_data()
    df = clean_data(df)
    X, y, scaler = preprocess_all_varieties(df)

    print(f"训练样本数：{len(X)}")
    model = create_lstm_model(X.shape[1:])
    early_stop = EarlyStopping(monitor='loss', patience=3)

    model.fit(X, y, epochs=20, batch_size=32, callbacks=[early_stop], verbose=1)
    model.save(MODEL_PATH)
    np.save(SCALER_PATH, scaler.min_, allow_pickle=False)
    np.save(SCALER_PATH.replace(".npy", "_scale.npy"), scaler.scale_, allow_pickle=False)

    print("模型训练完毕，已保存。")

# 运行训练
if __name__ == "__main__":
    train_unified_model()
