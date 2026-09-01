import pandas as pd

from utils.ballet_db import (
    add_ballet_class as db_add_ballet_class,
    get_all_ballet_classes as db_get_all_ballet_classes,
    update_ballet_class as db_update_ballet_class,
    delete_ballet_class as db_delete_ballet_class,
)


# ---------- CRUD ----------

def add_ballet_class(
    class_date,
    start_time,
    duration_hours,
    city,
    studio,
    address,
    teacher,
    class_type,
    level,
    notes,
):
    return db_add_ballet_class(
        class_date=class_date,
        start_time=start_time,
        duration_hours=duration_hours,
        city=city,
        studio=studio,
        address=address,
        teacher=teacher,
        class_type=class_type,
        level=level,
        notes=notes,
    )


def update_ballet_class(
    class_id,
    data,
):
    return db_update_ballet_class(
        class_id,
        data,
    )


def delete_ballet_class(class_id):
    return db_delete_ballet_class(
        class_id
    )


# ---------- Data Preparation ----------

def get_ballet_dataframe():
    records = db_get_all_ballet_classes()

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    df["class_date"] = pd.to_datetime(
        df["class_date"]
    )

    return df


# ---------- Filters ----------

def get_filter_options(df):
    return {
        "min_date": df["class_date"].min().date(),
        "max_date": df["class_date"].max().date(),

        "cities": (
            ["All"]
            + sorted(
                df["city"]
                .dropna()
                .unique()
                .tolist()
            )
        ),

        "teachers": (
            ["All"]
            + sorted(
                df["teacher"]
                .dropna()
                .unique()
                .tolist()
            )
        ),

        "studios": (
            ["All"]
            + sorted(
                df["studio"]
                .dropna()
                .unique()
                .tolist()
            )
        ),
    }


def filter_ballet_classes(
    df,
    start_date,
    end_date,
    city,
    teacher,
    studio,
):
    filtered_df = df[
        (df["class_date"].dt.date >= start_date)
        & (df["class_date"].dt.date <= end_date)
    ]

    if city != "All":
        filtered_df = filtered_df[
            filtered_df["city"] == city
        ]

    if teacher != "All":
        filtered_df = filtered_df[
            filtered_df["teacher"] == teacher
        ]

    if studio != "All":
        filtered_df = filtered_df[
            filtered_df["studio"] == studio
        ]

    return filtered_df


# ---------- Summary ----------

def get_ballet_summary(filtered_df):
    total_classes = len(filtered_df)

    total_hours = (
        filtered_df["duration_hours"].sum()
        if not filtered_df.empty
        else 0
    )

    return {
        "total_classes": total_classes,
        "total_hours": total_hours,
    }


# ---------- Status ----------

def get_ballet_status_tables(filtered_df):
    city_hours = (
        filtered_df
        .groupby(
            "city",
            dropna=False,
        )["duration_hours"]
        .sum()
        .reset_index()
        .sort_values(
            "duration_hours",
            ascending=False,
        )
    )

    teacher_hours = (
        filtered_df
        .groupby(
            "teacher",
            dropna=False,
        )["duration_hours"]
        .sum()
        .reset_index()
        .sort_values(
            "duration_hours",
            ascending=False,
        )
    )

    return {
        "city_hours": city_hours,
        "teacher_hours": teacher_hours,
    }

def get_ballet_dashboard_summary(today_date):
    df = get_ballet_dataframe()

    if df.empty:
        return {
            "total_hours": 0,
            "this_month_hours": 0,
            "last_class": None,
        }

    total_hours = df["duration_hours"].sum()

    month_mask = (
        (df["class_date"].dt.year == today_date.year)
        & (df["class_date"].dt.month == today_date.month)
    )

    this_month_hours = (
        df.loc[
            month_mask,
            "duration_hours",
        ].sum()
    )

    latest_row = (
        df
        .sort_values(
            "class_date",
            ascending=False,
        )
        .iloc[0]
    )

    last_class = latest_row.to_dict()
    last_class["class_date"] = str(
        latest_row["class_date"].date()
    )

    return {
        "total_hours": float(total_hours),
        "this_month_hours": float(this_month_hours),
        "last_class": last_class,
    }