import json

import urllib.request
import urllib.error

GRAFANA_URL = "http://localhost:3003"
DATASOURCE_UID = "cg06eccwhyepse"

with open(".grafana_token", "r") as f:
    GRAFANA_TOKEN = f.read().strip()

panels = []

def datasource():
    return {
        "type": "mysql",
        "uid": DATASOURCE_UID
    }

def stat_panel(panel_id, title, sql, x, y, w=4, h=4):
    return {
        "id": panel_id,
        "type": "stat",
        "title": title,
        "description": "Live KPI calculated from consumed Food Delivery streaming events stored in MySQL.",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": datasource(),
        "targets": [{
            "refId": "A",
            "format": "table",
            "rawSql": sql,
            "datasource": datasource()
        }],
        "options": {
            "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "",
                "values": False
            },
            "orientation": "auto",
            "textMode": "auto",
            "colorMode": "value"
        },
        "fieldConfig": {
            "defaults": {
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None}
                    ]
                }
            },
            "overrides": []
        }
    }

def chart_panel(panel_id, title, sql, x, y, w=8, h=7):
    return {
        "id": panel_id,
        "type": "timeseries",
        "title": title,
        "description": "Streaming order analytics derived from the consumed Kafka events.",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": datasource(),
        "targets": [{
            "refId": "A",
            "format": "time_series",
            "rawSql": sql,
            "datasource": datasource()
        }],
        "options": {
            "legend": {
                "displayMode": "list",
                "placement": "bottom"
            },
            "tooltip": {
                "mode": "multi",
                "sort": "desc"
            }
        },
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "smooth",
                    "lineWidth": 2,
                    "fillOpacity": 15,
                    "showPoints": "auto",
                    "spanNulls": True
                }
            },
            "overrides": []
        }
    }

def pie_panel(panel_id, title, sql, x, y):
    return {
        "id": panel_id,
        "type": "piechart",
        "title": title,
        "description": "Distribution of Food Delivery events across operational categories.",
        "gridPos": {"x": x, "y": y, "w": 6, "h": 7},
        "datasource": datasource(),
        "targets": [{
            "refId": "A",
            "format": "table",
            "rawSql": sql,
            "datasource": datasource()
        }],
        "options": {
            "pieType": "donut",
            "tooltip": {
                "mode": "single"
            },
            "legend": {
                "displayMode": "table",
                "placement": "right",
                "values": ["value", "percent"]
            }
        }
    }

def bar_panel(panel_id, title, sql, x, y):
    return {
        "id": panel_id,
        "type": "table",
        "title": title,
        "description": "Operational comparison across Food Delivery categories.",
        "gridPos": {
            "x": x,
            "y": y,
            "w": 12,
            "h": 7
        },
        "datasource": datasource(),
        "targets": [
            {
                "refId": "A",
                "format": "table",
                "rawSql": sql,
                "datasource": datasource()
            }
        ],
        "options": {
            "showHeader": True,
            "cellHeight": "sm"
        },
        "fieldConfig": {
            "defaults": {},
            "overrides": []
        }
    }

# KPI row
panels.append(stat_panel(
    1,
    "Total Orders",
    "SELECT COUNT(*) AS total_orders FROM orders;",
    0, 0
))

panels.append(stat_panel(
    2,
    "Total Revenue",
    "SELECT ROUND(SUM(order_value),2) AS total_revenue FROM orders;",
    4, 0
))

panels.append(stat_panel(
    3,
    "Average Order Value",
    "SELECT ROUND(AVG(order_value),2) AS average_order_value FROM orders;",
    8, 0
))

panels.append(stat_panel(
    4,
    "Successful Payments",
    "SELECT ROUND(100.0 * SUM(payment_status='SUCCESS') / COUNT(*),2) AS success_rate FROM orders;",
    12, 0
))

panels.append(stat_panel(
    5,
    "Failed Payments",
    "SELECT SUM(payment_status='FAILED') AS failed_payments FROM orders;",
    16, 0
))

# Time series
panels.append(chart_panel(
    6,
    "Orders Over Time",
    """
    SELECT
        order_time AS time,
        COUNT(*) AS orders
    FROM orders
    WHERE $__timeFilter(order_time)
    GROUP BY order_time
    ORDER BY order_time;
    """,
    0, 4, 12, 7
))

panels.append(chart_panel(
    7,
    "Revenue Over Time",
    """
    SELECT
        order_time AS time,
        SUM(order_value) AS revenue
    FROM orders
    WHERE $__timeFilter(order_time)
    GROUP BY order_time
    ORDER BY order_time;
    """,
    12, 4, 12, 7
))

# Restaurant
panels.append(bar_panel(
    8,
    "Orders by Restaurant",
    """
    SELECT
        restaurant_id AS restaurant,
        COUNT(*) AS orders
    FROM orders
    GROUP BY restaurant_id
    ORDER BY orders DESC;
    """,
    0, 11
))

# Status distributions
panels.append(pie_panel(
    9,
    "Order Status Distribution",
    """
    SELECT
        order_status AS status,
        COUNT(*) AS total
    FROM orders
    GROUP BY order_status
    ORDER BY total DESC;
    """,
    12, 11
))

panels.append(pie_panel(
    10,
    "Payment Status Distribution",
    """
    SELECT
        payment_status AS status,
        COUNT(*) AS total
    FROM orders
    GROUP BY payment_status
    ORDER BY total DESC;
    """,
    18, 11
))

# Delivery partners
panels.append(bar_panel(
    11,
    "Orders by Delivery Partner",
    """
    SELECT
        delivery_partner_id AS delivery_partner,
        COUNT(*) AS orders
    FROM orders
    GROUP BY delivery_partner_id
    ORDER BY orders DESC;
    """,
    0, 18
))

# AOV by restaurant
panels.append(bar_panel(
    12,
    "Average Order Value by Restaurant",
    """
    SELECT
        restaurant_id AS restaurant,
        ROUND(AVG(order_value),2) AS average_order_value
    FROM orders
    GROUP BY restaurant_id
    ORDER BY average_order_value DESC;
    """,
    0, 25
))

dashboard = {
    "dashboard": {
        "id": None,
        "uid": "food-delivery-streaming",
        "title": "Food Delivery — Real-Time Operations Dashboard",
        "tags": [
            "assignment-2",
            "food-delivery",
            "kafka",
            "streaming",
            "business-analytics"
        ],
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 1,
        "refresh": "5s",
        "time": {
            "from": "2026-08-16T18:00:00Z",
            "to": "2026-08-16T20:00:00Z"
        },
        "panels": panels,
        "templating": {
            "list": []
        },
        "annotations": {
            "list": []
        },
        "editable": True
    },
    "folderId": 0,
    "overwrite": True
}

data = json.dumps(dashboard).encode("utf-8")

request = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=data,
    headers={
        "Content-Type": "application/json"
    },
    method="POST"
)

request.add_header(
    "Authorization",
    f"Bearer {GRAFANA_TOKEN}"
)

opener = urllib.request.build_opener()

try:
    response = opener.open(request)
    result = response.read().decode("utf-8")
    print("Dashboard created successfully.")
    print(result)
except urllib.error.HTTPError as e:
    print("Grafana API returned an error:")
    print(e.read().decode("utf-8"))
except Exception as e:
    print("Error:")
    print(e)
