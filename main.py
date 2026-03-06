import time
import requests
import json
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────

GOOGLE_CHAT_WEBHOOKS = [
    "https://chat.googleapis.com/v1/spaces/AAQAGhxWZZM/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=IZg6yXQqGqRyXvBE26DX6t_E6IGJnKZoDokjzyjmY2E",
    "https://chat.googleapis.com/v1/spaces/AAQAgdDJy_E/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=Vh0L5WfIwKGBgkjw8_IahWLnZpJPBx433T4KKtA6E44",
]

POLL_INTERVAL_SECONDS = 5
FILTER_AREAS = []  # ריק = הכל

# ─────────────────────────────────────────────
#  PIKUD HAOREF API
# ─────────────────────────────────────────────

OREF_URL = "https://www.oref.org.il/WarningMessages/alert/alerts.json"

HEADERS = {
    "Referer": "https://www.oref.org.il/",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0",
}

last_alert_id = None


def fetch_active_alerts():
    try:
        response = requests.get(OREF_URL, headers=HEADERS, timeout=5)
        if response.status_code == 200 and response.text.strip():
            text = response.text.lstrip("\ufeff").strip()
            if text:
                return json.loads(text)
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"[!] שגיאה: {e}")
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
        return False
    if FILTER_AREAS:
        alert_areas = alert.get("data", [])
        if not any(area in alert_areas for area in FILTER_AREAS):
            return False
    return True


def send_to_google_chat(message: str):
    payload = {"text": message}
    for i, webhook in enumerate(GOOGLE_CHAT_WEBHOOKS, 1):
        try:
            response = requests.post(webhook, json=payload, timeout=10)
            response.raise_for_status()
            print(f"[✓] נשלח ל-Webhook #{i}")
        except requests.RequestException as e:
            print(f"[✗] שגיאה ל-Webhook #{i}: {e}")


def main():
    global last_alert_id
    print(f"🟢 מאזין לפיקוד העורף (כל {POLL_INTERVAL_SECONDS} שניות)...")

    while True:
        alert = fetch_active_alerts()
        if alert and isinstance(alert, dict) and alert.get("data"):
            if should_notify(alert):
                alert_id = alert.get("id", "")
                print(f"[🚨] התראה חדשה! ID: {alert_id}")
                send_to_google_chat(format_alert_message(alert))
                last_alert_id = alert_id
        else:
            print(f"[✓] {datetime.now().strftime('%H:%M:%S')} – שקט", end="\r")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
