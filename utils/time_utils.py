from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

BJ_TZ = ZoneInfo("Asia/Shanghai")

def today_bj_date():
    return datetime.now(BJ_TZ).date()

def now_bj_iso():
    return datetime.now(BJ_TZ).isoformat()


def format_bj_time(value):
    if not value:
        return ""

    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(BJ_TZ).strftime("%Y-%m-%d %H:%M:%S")


def beijing_day_utc_range(date_str):
    start_bj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=BJ_TZ)
    end_bj = start_bj + timedelta(days=1)

    return (
        start_bj.astimezone(timezone.utc).isoformat(),
        end_bj.astimezone(timezone.utc).isoformat()
    )