import json
import os
import time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen


API_BASE_URL = os.getenv("API_BASE_URL", "http://app:8000").rstrip("/")
SCHEDULE_TIME = os.getenv("REMINDER_SCHEDULE_TIME", "08:00")


def _parse_schedule_time(value: str):
    try:
        hour_str, minute_str = value.split(":")
        hour = int(hour_str)
        minute = int(minute_str)
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError
        return hour, minute
    except ValueError:
        raise ValueError("REMINDER_SCHEDULE_TIME deve estar no formato HH:MM")


def _seconds_until_next_run(hour: int, minute: int):
    now = datetime.now()
    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if next_run <= now:
        next_run = next_run + timedelta(days=1)
    return (next_run - now).total_seconds(), next_run


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
    hour, minute = _parse_schedule_time(SCHEDULE_TIME)
    print(f"[scheduler] Iniciado. API={API_BASE_URL} horario={SCHEDULE_TIME}")

    while True:
        wait_seconds, next_run = _seconds_until_next_run(hour, minute)
        print(f"[scheduler] Proxima execucao em {int(wait_seconds)}s ({next_run.isoformat()})")
        time.sleep(wait_seconds)

        try:
            result = _send_due_reminders()
            print(f"[scheduler] Execucao concluida: {result}")
        except Exception as exc:
            print(f"[scheduler] Falha ao processar lembretes: {exc}")


if __name__ == "__main__":
    main()
