from utils.supabase_client import get_supabase_client


def get_options(option_group, include_inactive=False):
    supabase = get_supabase_client()

    query = (
        supabase
        .table("nook_options")
        .select("*")
        .eq("option_group", option_group)
        .order("sort_order", desc=False)
        .order("label", desc=False)
    )

    if not include_inactive:
        query = query.eq("is_active", True)

    result = query.execute()
    return result.data


def get_option_labels(option_group, include_other=True):
    options = get_options(option_group)
    labels = [item["label"] for item in options]

    if include_other and "Other" not in labels:
        labels.append("Other")

    return labels


def add_option(option_group, label, sort_order=0, notes=""):
    supabase = get_supabase_client()

    value = label.strip()

    return supabase.table("nook_options").insert({
        "option_group": option_group,
        "label": label.strip(),
        "value": value,
        "sort_order": sort_order,
        "notes": notes.strip() if notes else None,
        "is_active": True,
    }).execute()


def update_option_status(option_id, is_active):
    supabase = get_supabase_client()

    return (
        supabase
        .table("nook_options")
        .update({"is_active": is_active})
        .eq("id", option_id)
        .execute()
    )


def delete_option(option_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("nook_options")
        .delete()
        .eq("id", option_id)
        .execute()
    )