import json
from kafka import KafkaConsumer

TOPIC = "food_delivery_orders"
BOOTSTRAP_SERVERS = "localhost:9092"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="food_delivery_assignment2_consumer",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print(f"Connected to Kafka at {BOOTSTRAP_SERVERS}")
print(f"Reading from topic: {TOPIC}")
print("-" * 70)

count = 0

for message in consumer:
    record = message.value
    count += 1

    print(
        f"Order: {record['order_id']} | "
        f"Customer: {record['customer_id']} | "
        f"Restaurant: {record['restaurant_id']} | "
        f"Value: ₹{record['order_value']} | "
        f"Status: {record['order_status']}"
    )

    if count >= 10:
        break

consumer.close()

print("-" * 70)
print(f"Consumer successfully processed {count} messages.")
