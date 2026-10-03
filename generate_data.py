import csv
import random
from datetime import datetime, timedelta

random.seed(42)

restaurants = [f"REST{200 + i}" for i in range(1, 21)]
customers = [f"CUS{500 + i}" for i in range(1, 51)]
delivery_partners = [f"DP{700 + i}" for i in range(1, 31)]

payment_statuses = ["SUCCESS", "SUCCESS", "SUCCESS", "FAILED", "PENDING"]

order_statuses = [
    "PLACED",
    "CONFIRMED",
    "PREPARING",
    "OUT_FOR_DELIVERY",
    "DELIVERED"
]

start_time = datetime(2026, 8, 16, 18, 0, 0)

with open("sample_data.csv", "w", newline="") as file:

    fieldnames = [
        "order_id",
        "customer_id",
        "restaurant_id",
        "delivery_partner_id",
        "order_value",
        "order_time",
        "latitude",
        "longitude",
        "payment_status",
        "order_status"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(1, 101):

        order_time = start_time + timedelta(seconds=i * 45)

        writer.writerow({
            "order_id": f"ORD{10000 + i}",
            "customer_id": random.choice(customers),
            "restaurant_id": random.choice(restaurants),
            "delivery_partner_id": random.choice(delivery_partners),
            "order_value": random.randint(150, 1500),
            "order_time": order_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "latitude": round(random.uniform(28.55, 28.70), 6),
            "longitude": round(random.uniform(77.10, 77.30), 6),
            "payment_status": random.choice(payment_statuses),
            "order_status": random.choice(order_statuses)
        })

print("sample_data.csv created successfully.")
print("Records created: 100")
