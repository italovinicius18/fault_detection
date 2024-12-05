import json
import random
import time
from kafka import KafkaProducer
from datetime import datetime

def generate_random_data():
    data = {
        'x': random.uniform(0, 100),
        'y': random.uniform(0, 100),
        'z': random.uniform(0, 100),
        'timestamp': datetime.now()
    }
    return data

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

if __name__ == "__main__":
    producer = KafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=json_serializer
    )

    while True:
        data = generate_random_data()
        producer.send('vibration-data', value=data)
        print(f"Mensagem enviada: {data}")
        time.sleep(1)  # Ajuste o tempo conforme necessário
