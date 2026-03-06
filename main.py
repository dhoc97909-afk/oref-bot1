import time
import requests
import json
from datetime import datetime

GOOGLE_CHAT_WEBHOOKS = [
    "https://chat.googleapis.com/v1/spaces/AAQAGhxWZZM/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=IZg6yXQqGqRyXvBE26DX6t_E6IGJnKZoDokjzyjmY2E",
    "https://chat.googleapis.com/v1/spaces/AAQAgdDJy_E/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=Vh0L5WfIwKGBgkjw8_IahWLnZpJPBx433T4KKtA6E44",
]

POLL_INTERVAL_SECONDS = 5
FILTER_AREAS = []

# API חלופי פתוח שלא חוסם IPs זרים
TZEVA_ADOM_URL = "https://api.tzevaadom.co.il/alerts"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

last_alert_ids = set()


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def fetch_active_alerts():
    try:
        response = requests.get(TZEVA_ADOM_URL, headers=HEADERS, timeout=5)
        log(f"API status: {response.status_code} | body: '{response.text[:200]}'")
        if response.status_code == 200 and response.text.strip():
            return response.json()
    except (requests.RequestException, json.JSONDecodeError) as e:
        log(f"שגיאה: {e}")
    return None


def format_alert_message(alert) -> str:
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # tzevaadom API מחזיר רשימת ערים ישירות
    if isinstance(alert, list):
        areas = alert
        title = "התראת צבע אדום"
    else:
        areas = alert.get("cities", alert.get("data", []))
        title = alert.get("title", "התראת צבע אדום")

    areas_text = "\n".join(f"  • {area}" for area in areas) if areas else "  • לא ידוע"
    return (
        f"🚨 *{title}* 🚨\n"
        f"🕐 {now}\n\n"
        f"📍 *אזורים מוזהרים:*\n{areas_text}"
    )


def send_to_google_chat(message: str):
    payload = {"text": message}
    for i, webhook in enumerate(GOOGLE_CHAT_WEBHOOKS, 1):
        try:
            response = requests.post(webhook, json=payload, timeout=10)
            response.raise_for_status()
            log(f"נשלח ל-Webhook #{i}")
        except requests.RequestException as e:
            log(f"שגיאה ל-Webhook #{i}: {e}")


def main():
    global last_alert_ids
    log("מאזין להתראות צבע אדום...")

    while True:
        data = fetch_active_alerts()

        if data:
            # API מחזיר רשימה של התראות או אובייקט בודד
            alerts = data if isinstance(data, list) else [data]

            for alert in alerts:
                # יצירת מזהה ייחודי מהתוכן
                cities = alert.get("cities", alert.get("data", []))
                if not cities:
                    continue

                alert_key = frozenset(cities)

                if alert_key not in last_alert_ids:
                    log(f"התראה חדשה: {cities}")
                    send_to_google_chat(format_alert_message(alert))
                    last_alert_ids.add(alert_key)
        else:
            # אם אין התראות — נקה את הזיכרון לקראת הפעם הבאה
            last_alert_ids = set()

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
    
