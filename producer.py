import csv
import json
import time
from kafka import KafkaProducer

TOPIC = "food_delivery_orders"
BOOTSTRAP_SERVERS = "localhost:9092"

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print(f"Connected to Kafka at {BOOTSTRAP_SERVERS}")
print(f"Sending records to topic: {TOPIC}")
print("-" * 60)

with open("sample_data.csv", "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        future = producer.send(TOPIC, value=row)
        metadata = future.get(timeout=10)

        print(
            f"Sent: {row['order_id']} | "
            f"Partition: {metadata.partition} | "
            f"Offset: {metadata.offset}"
        )

        time.sleep(0.2)

producer.flush()
producer.close()

print("-" * 60)
print("All records sent successfully.")

