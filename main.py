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

OREF_URL = "https://www.oref.org.il/WarningMessages/alert/alerts.json"

HEADERS = {
    "Referer": "https://www.oref.org.il/",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0",
}

last_alert_id = None


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def fetch_active_alerts():
    try:
        response = requests.get(OREF_URL, headers=HEADERS, timeout=5)
        log(f"API status: {response.status_code} | body: '{response.text[:200]}'")
        if response.status_code == 200 and response.text.strip():
            text = response.text.lstrip("\ufeff").strip()
            if text:
                return json.loads(text)
    except (requests.RequestException, json.JSONDecodeError) as e:
        log(f"שגיאה: {e}")
    return None


def format_alert_message(alert: dict) -> str:
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    areas = alert.get("data", [])
    title = alert.get("title", "התראת צבע אדום")
    desc = alert.get("desc", "")
    areas_text = "\n".join(f"  • {area}" for area in areas) if areas else "  • לא ידוע"
    return (
        f"🚨 *{title}* 🚨\n"
        f"🕐 {now}\n\n"
        f"📍 *אזורים מוזהרים:*\n{areas_text}\n\n"
        f"ℹ️ {desc}"
    )


def should_notify(alert: dict) -> bool:
    global last_alert_id
    alert_id = alert.get("id", "")
    if alert_id == last_alert_id:
        log(f"כפילות – אותו ID: {alert_id}, מדלג")
        return False
    if FILTER_AREAS:
        alert_areas = alert.get("data", [])
        if not any(area in alert_areas for area in FILTER_AREAS):
            log(f"אזור לא רלוונטי: {alert_areas}")
            return False
    return True


def send_to_google_chat(message: str):
    payload = {"text": message}
    for i, webhook in enumerate(GOOGLE_CHAT_WEBHOOKS, 1):
        try:
            response = requests.post(webhook, json=payload, timeout=10)
            response.raise_for_status()
            log(f"✓ נשלח ל-Webhook #{i}")
        except requests.RequestException as e:
            log(f"✗ שגיאה ל-Webhook #{i}: {e}")


def main():
    global last_alert_id
    log("🟢 מאזין לפיקוד העורף...")

    while True:
        alert = fetch_active_alerts()
        if alert and isinstance(alert, dict) and alert.get("data"):
            log(f"🚨 התראה: {json.dumps(alert, ensure_ascii=False)}")
            if should_notify(alert):
                send_to_google_chat(format_alert_message(alert))
                last_alert_id = alert.get("id", "")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
