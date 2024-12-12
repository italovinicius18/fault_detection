import polars as pl
import json
import time
from datetime import datetime
import random
from kafka import KafkaProducer

CHUNK_SIZE = 10

# Função para adicionar ruído a um valor numérico
def add_noise(value, noise_level=0.01):
    # noise_level = 0.01 significa até ±1% de variação
    factor = 1 + random.uniform(-noise_level, noise_level)
    return value * factor

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Ler o CSV com Polars
df = pl.read_csv("ai4i2020.csv")

rows = df.iter_rows(named=True)
chunk = []

for row in rows:
    data = {
        # Aqui aplicamos ruído a cada coluna numérica
        "air_temp_k": add_noise(float(row["Air temperature [K]"]), 0.02),
        "process_temp_k": add_noise(float(row["Process temperature [K]"]), 0.02),
        "rotational_speed_rpm": add_noise(float(row["Rotational speed [rpm]"]), 0.02),
        "torque_nm": add_noise(float(row["Torque [Nm]"]), 0.02),
        "tool_wear_min": add_noise(float(row["Tool wear [min]"]), 0.05),
        "machine_failure": int(row["Machine failure"]),
        "product_id": row["Product ID"],
        "type": row["Type"],
        "timestamp": datetime.now().astimezone().isoformat()
    }

    chunk.append(data)

    if len(chunk) == CHUNK_SIZE:
        producer.send('milling-data', value=chunk)
        time.sleep(1)
        chunk = []

if chunk:
    producer.send('milling-data', value=chunk)
    time.sleep(1)

producer.flush()
