from utils.supabase_client import get_supabase_client


# ---------- Ballet ----------

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
    supabase = get_supabase_client()

    return (
        supabase
        .table("ballet_classes")
        .insert({
            "class_date": class_date,
            "start_time": start_time,
            "duration_hours": duration_hours,
            "city": city,
            "studio": studio,
            "address": address,
            "teacher": teacher,
            "class_type": class_type,
            "level": level,
            "notes": notes,
        })
        .execute()
    )


def get_all_ballet_classes():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("ballet_classes")
        .select("*")
        .order("class_date", desc=True)
        .execute()
    )

    return result.data


def update_ballet_class(
    class_id,
    data,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("ballet_classes")
        .update(data)
        .eq("id", class_id)
        .execute()
    )


def delete_ballet_class(class_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("ballet_classes")
        .delete()
        .eq("id", class_id)
        .execute()
    )