import json
import os
from urllib.request import Request, urlopen


API_BASE_URL = os.getenv("API_BASE_URL", "http://app:8000").rstrip("/")
SCHEDULE_TIME = os.getenv("REMINDER_SCHEDULE_TIME", "08:00")
REMINDER_SCHEDULE_TIME = SCHEDULE_TIME


def _send_due_reminders():
    url = f"{API_BASE_URL}/reminders/send-due"
    payload = json.dumps({}).encode("utf-8")
    request = Request(
        url=url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
        return body


def main():
    print(f"[scheduler] Iniciado. API={API_BASE_URL}")

    try:
        result = _send_due_reminders()
        print(f"[scheduler] Execucao concluida: {result}")
    except Exception as exc:
        print(f"[scheduler] Falha ao processar lembretes: {exc}")


if __name__ == "__main__":
    main()
