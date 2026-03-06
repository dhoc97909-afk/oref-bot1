import time
import json
from datetime import datetime
import requests
import tzevaadom

GOOGLE_CHAT_WEBHOOKS = [
    "https://chat.googleapis.com/v1/spaces/AAQAGhxWZZM/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=IZg6yXQqGqRyXvBE26DX6t_E6IGJnKZoDokjzyjmY2E",
    "https://chat.googleapis.com/v1/spaces/AAQAgdDJy_E/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=Vh0L5WfIwKGBgkjw8_IahWLnZpJPBx433T4KKtA6E44",
]


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def send_to_google_chat(message: str):
    payload = {"text": message}
    for i, webhook in enumerate(GOOGLE_CHAT_WEBHOOKS, 1):
        try:
            response = requests.post(webhook, json=payload, timeout=10)
            response.raise_for_status()
            log(f"נשלח ל-Webhook #{i}")
        except requests.RequestException as e:
            log(f"שגיאה ל-Webhook #{i}: {e}")


def handle_alert(alerts):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log(f"התראה חדשה: {alerts}")

    areas_text = "\n".join(f"  • {a['name']}" for a in alerts) if alerts else "  • לא ידוע"

    message = (
        f"🚨 *התראת צבע אדום* 🚨\n"
        f"🕐 {now}\n\n"
        f"📍 *אזורים מוזהרים:*\n{areas_text}"
    )
    send_to_google_chat(message)


log("מאזין להתראות צבע אדום...")
tzevaadom.alerts_listener(handle_alert)

# שמור את התהליך פעיל
while True:
    time.sleep(60)
