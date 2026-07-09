from utils.supabase_client import get_supabase_client
from services.supplement_service import enrich_bottle_with_remaining


def get_low_stock_supplement_bottles(threshold=10):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplement_bottles")
        .select("*, supplements(name)")
        .eq("status", "active")
        .execute()
    )

    low_stock = []

    for bottle in result.data:
        enriched = enrich_bottle_with_remaining(bottle)

        if enriched["remaining"] <= threshold:
            supplement = enriched.get("supplements") or {}

            low_stock.append({
                "supplement_name": supplement.get("name") or "",
                "brand": enriched.get("brand") or "",
                "product_name": enriched.get("product_name") or "",
                "remaining": enriched["remaining"],
                "unit": enriched.get("unit") or "",
            })

    return low_stock