import json
import mysql.connector
from kafka import KafkaConsumer

TOPIC = "food_delivery_orders"
BOOTSTRAP_SERVERS = "localhost:9092"

# Connect to MySQL
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3309,
    user="fooduser",
    password="foodpass",
    database="food_delivery"
)

cursor = db.cursor()

print("Connected to MySQL")
print(f"Connected to Kafka at {BOOTSTRAP_SERVERS}")
print(f"Reading from topic: {TOPIC}")
print("-" * 80)

# Connect to Kafka
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="food_delivery_assignment2_mysql_consumer",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

count = 0

for message in consumer:
    record = message.value

    sql = """
        INSERT INTO orders (
            order_id,
            customer_id,
            restaurant_id,
            delivery_partner_id,
            order_value,
            order_time,
            latitude,
            longitude,
            payment_status,
            order_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            customer_id = VALUES(customer_id),
            restaurant_id = VALUES(restaurant_id),
            delivery_partner_id = VALUES(delivery_partner_id),
            order_value = VALUES(order_value),
            order_time = VALUES(order_time),
            latitude = VALUES(latitude),
            longitude = VALUES(longitude),
            payment_status = VALUES(payment_status),
            order_status = VALUES(order_status)
    """

    values = (
        record["order_id"],
        record["customer_id"],
        record["restaurant_id"],
        record["delivery_partner_id"],
        float(record["order_value"]),
        record["order_time"],
        float(record["latitude"]),
        float(record["longitude"]),
        record["payment_status"],
        record["order_status"]
    )

    cursor.execute(sql, values)
    db.commit()

    count += 1

    print(
        f"Consumed: {record['order_id']} | "
        f"Restaurant: {record['restaurant_id']} | "
        f"Value: ₹{record['order_value']} | "
        f"Payment: {record['payment_status']} | "
        f"Status: {record['order_status']}"
    )

    # Process all 100 records already in Kafka
    if count >= 100:
        break

consumer.close()
cursor.close()
db.close()

print("-" * 80)
print(f"Consumer successfully processed {count} messages.")
print("Records inserted into MySQL successfully.")
