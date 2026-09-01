from utils.supabase_client import get_supabase_client


def enrich_bottle_with_remaining(bottle):
    remaining = calculate_bottle_remaining(
        bottle["id"],
        bottle.get("initial_quantity")
        or bottle.get("quantity"),
    )

    enriched = bottle.copy()
    enriched["remaining"] = remaining

    return enriched


def build_bottle_label(
    supplement,
    bottle,
):
    remaining = bottle.get("remaining")

    label_parts = [
        supplement.get("name") or "",
        bottle.get("brand") or "",
        bottle.get("product_name") or "",
        bottle.get("strength") or "",
    ]

    if remaining is not None:
        label_parts.append(
            f"{remaining:g} left"
        )

    if bottle.get("expiry_date"):
        label_parts.append(
            f'exp {bottle["expiry_date"]}'
        )

    return " | ".join([
        part
        for part in label_parts
        if part
    ])


def calculate_bottle_remaining(
    bottle_id,
    initial_quantity,
):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplement_intakes")
        .select("amount")
        .eq("bottle_id", bottle_id)
        .execute()
    )

    used = sum(
        float(item["amount"] or 0)
        for item in result.data
    )

    initial = float(
        initial_quantity or 0
    )

    return max(
        initial - used,
        0,
    )