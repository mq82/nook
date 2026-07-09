from utils.supplement_db import calculate_bottle_remaining


def enrich_bottle_with_remaining(bottle):
    remaining = calculate_bottle_remaining(
        bottle["id"],
        bottle.get("initial_quantity") or bottle.get("quantity")
    )

    enriched = bottle.copy()
    enriched["remaining"] = remaining

    return enriched


def build_bottle_label(supplement, bottle):
    remaining = bottle.get("remaining")

    label_parts = [
        supplement.get("name") or "",
        bottle.get("brand") or "",
        bottle.get("product_name") or "",
        bottle.get("strength") or "",
    ]

    if remaining is not None:
        label_parts.append(f"{remaining:g} left")

    if bottle.get("expiry_date"):
        label_parts.append(f'exp {bottle["expiry_date"]}')

    return " | ".join([part for part in label_parts if part])