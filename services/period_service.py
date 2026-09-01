import pandas as pd

from datetime import timedelta
from utils.time_utils import today_bj_date
from utils.period_db import (
    upsert_period_record as db_upsert_period_record,
    get_all_period_records as db_get_all_period_records,
    update_period_record as db_update_period_record,
    delete_period_record as db_delete_period_record,
    upsert_period_records as db_upsert_period_records,
    upsert_daily_log as db_upsert_daily_log,
    get_daily_logs as db_get_daily_logs,
    update_daily_log as db_update_daily_log,
    delete_daily_log as db_delete_daily_log,
)


# ---------- Period Records ----------

def save_period_record(
    start_date,
    end_date,
    flow_level,
    notes,
):
    data = {
        "start_date": str(start_date),
        "end_date": (
            str(end_date)
            if end_date
            else None
        ),
        "flow_level": flow_level or None,
        "source": "manual",
        "notes": notes or None,
    }

    return db_upsert_period_record(
        data
    )


def get_period_history_dataframe():
    records = db_get_all_period_records()

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    df["start_date"] = pd.to_datetime(
        df["start_date"]
    )

    df["end_date"] = pd.to_datetime(
        df["end_date"],
        errors="coerce",
    )

    df = df.sort_values(
        "start_date",
        ascending=False,
    )

    df["period_length_days"] = (
        df["end_date"]
        - df["start_date"]
    ).dt.days + 1

    df_asc = df.sort_values(
        "start_date"
    ).copy()

    df_asc["cycle_length_days"] = (
        df_asc["start_date"]
        .diff()
        .dt.days
    )

    cycle_length_map = (
        df_asc
        .set_index("id")["cycle_length_days"]
        .to_dict()
    )

    df["cycle_length_days"] = (
        df["id"]
        .map(cycle_length_map)
    )

    return df


def get_period_summary(df):
    if df.empty:
        return {
            "avg_cycle_length": None,
            "avg_period_length": None,
            "current_cycle_day": None,
            "latest_start": None,
        }

    recent_cycle_lengths = (
        df["cycle_length_days"]
        .dropna()
        .head(6)
    )

    recent_period_lengths = (
        df["period_length_days"]
        .dropna()
        .head(6)
    )

    avg_cycle_length = (
        recent_cycle_lengths.mean()
        if not recent_cycle_lengths.empty
        else None
    )

    avg_period_length = (
        recent_period_lengths.mean()
        if not recent_period_lengths.empty
        else None
    )

    latest_record = (
        df
        .sort_values(
            "start_date",
            ascending=False,
        )
        .iloc[0]
    )

    latest_start = (
        latest_record["start_date"]
        .date()
    )

    current_cycle_day = (
        today_bj_date()
        - latest_start
    ).days + 1

    return {
        "avg_cycle_length": avg_cycle_length,
        "avg_period_length": avg_period_length,
        "current_cycle_day": current_cycle_day,
        "latest_start": latest_start,
    }


def update_period_record(
    record_id,
    data,
):
    return db_update_period_record(
        record_id,
        data,
    )


def delete_period_record(
    record_id,
):
    return db_delete_period_record(
        record_id
    )


# ---------- CSV Import ----------

def clean_period_csv(df):
    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    required_columns = [
        "start_date",
        "end_date",
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Missing required column: {column}"
            )

    df["start_date"] = pd.to_datetime(
        df["start_date"],
        errors="coerce",
    ).dt.date

    df["end_date"] = pd.to_datetime(
        df["end_date"],
        errors="coerce",
    ).dt.date

    if "flow_level" not in df.columns:
        df["flow_level"] = None

    if "notes" not in df.columns:
        df["notes"] = None

    df = df.dropna(
        subset=["start_date"]
    )

    df = df.drop_duplicates(
        subset=["start_date"]
    )

    records = []

    for _, row in df.iterrows():
        records.append({
            "start_date": str(
                row["start_date"]
            ),
            "end_date": (
                str(row["end_date"])
                if pd.notna(row["end_date"])
                else None
            ),
            "flow_level": (
                row["flow_level"]
                if pd.notna(row["flow_level"])
                else None
            ),
            "source": "csv_import",
            "notes": (
                row["notes"]
                if pd.notna(row["notes"])
                else None
            ),
        })

    return records


def import_period_records(df):
    records = clean_period_csv(
        df
    )

    if not records:
        return 0

    db_upsert_period_records(
        records
    )

    return len(records)


# ---------- Daily Logs ----------

def save_daily_log(
    log_date,
    sleep_hours,
    energy_level,
    stress_level,
    mood,
    lower_ab_pain,
    notes,
):
    data = {
        "log_date": str(log_date),
        "sleep_hours": sleep_hours,
        "energy_level": energy_level,
        "stress_level": stress_level,
        "mood": mood,
        "lower_ab_pain": lower_ab_pain,
        "notes": notes or None,
    }

    return db_upsert_daily_log(
        data
    )


def get_daily_logs_dataframe(
    limit=30,
):
    records = db_get_daily_logs(
        limit
    )

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(
        records
    )


def update_daily_log(
    log_id,
    data,
):
    return db_update_daily_log(
        log_id,
        data,
    )


def delete_daily_log(
    log_id,
):
    return db_delete_daily_log(
        log_id
    )


def get_period_dashboard_summary(today_date):
    df = get_period_history_dataframe()

    if df.empty:
        return {
            "cycle_day": None,
            "latest_period_start": None,
            "latest_period_end": None,
            "predicted_next_period": None,
            "days_until_next_period": None,
            "today_daily_log": None,
        }

    # ---------- Latest Period ----------

    latest = (
        df
        .sort_values(
            "start_date",
            ascending=False,
        )
        .iloc[0]
    )

    latest_period_start = (
        latest["start_date"].date()
    )

    latest_period_end = (
        latest["end_date"].date()
        if pd.notna(latest["end_date"])
        else None
    )

    cycle_day = (
        today_date
        - latest_period_start
    ).days + 1

    # ---------- Prediction ----------

    recent_cycle_lengths = (
        df["cycle_length_days"]
        .dropna()
        .head(6)
    )

    predicted_next_period = None
    days_until_next_period = None

    if not recent_cycle_lengths.empty:
        avg_cycle = int(
            round(
                recent_cycle_lengths.mean()
            )
        )

        predicted_next_period = (
            latest_period_start
            + timedelta(days=avg_cycle)
        )

        days_until_next_period = (
            predicted_next_period
            - today_date
        ).days

    # ---------- Today's Daily Log ----------

    daily_logs = get_daily_logs_dataframe(
        limit=30
    )

    today_daily_log = None

    if not daily_logs.empty:
        today_str = str(today_date)

        today_rows = daily_logs[
            daily_logs["log_date"].astype(str)
            == today_str
        ]

        if not today_rows.empty:
            today_daily_log = (
                today_rows.iloc[0].to_dict()
            )

    return {
        "cycle_day": cycle_day,
        "latest_period_start": latest_period_start,
        "latest_period_end": latest_period_end,
        "predicted_next_period": predicted_next_period,
        "days_until_next_period": days_until_next_period,
        "today_daily_log": today_daily_log,
    }