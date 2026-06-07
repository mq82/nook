import sys
from pathlib import Path

import streamlit as st
import pandas as pd
from datetime import date, datetime, timezone

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from utils.supabase_client import get_supabase_client

def render_pingping_checkin():
    st.subheader("Pingping Daily Check")

    supabase = get_supabase_client()

    checkin_date = st.date_input("Check-in Date", value=date.today())

    plans_result = (
        supabase
        .table("pingping_supplement_plans")
        .select("*")
        .eq("is_active", True)
        .lte("start_date", str(checkin_date))
        .or_(f"end_date.is.null,end_date.gte.{str(checkin_date)}")
        .order("timing", desc=False)
        .execute()
    )

    plans = plans_result.data

    if not plans:
        st.info("No active supplement plans for this date.")
        return
    
    checkin_result = (
        supabase
        .table("pingping_supplement_checkins")
        .select("*")
        .eq("checkin_date", str(checkin_date))
        .execute()
    )

    existing_checkins = {
        item["plan_id"]: item
        for item in checkin_result.data
    }

    st.write(f"Plans for {checkin_date}")

    for plan in plans:
        plan_id = plan["id"]
        existing = existing_checkins.get(plan_id)
        already_taken = existing["is_taken"] if existing else False

        label = f'{plan["timing"] or "No timing"} - {plan["supplement_name"]} - {plan["dosage"] or ""} - {plan["frequency"] or ""}'

        taken = st.checkbox(
            label,
            value=already_taken,
            key=f"pingping_checkin_{plan_id}_{checkin_date}"
        )

        if taken != already_taken:
            if existing:
                supabase.table("pingping_supplement_checkins").update({
                    "is_taken": taken,
                    "taken_at": datetime.now(timezone.utc).isoformat() if taken else None
                }).eq("id", existing["id"]).execute()
            else:
                supabase.table("pingping_supplement_checkins").insert({
                    "plan_id": plan_id,
                    "checkin_date": str(checkin_date),
                    "is_taken": taken,
                    "taken_at": datetime.now(timezone.utc).isoformat() if taken else None
                }).execute()

            st.rerun()
        
    st.divider()

    total = len(plans)

    fresh_checkins_result = (
        supabase
        .table("pingping_supplement_checkins")
        .select("*")
        .eq("checkin_date", str(checkin_date))
        .eq("is_taken", True)
        .execute()
    )

    fresh_checkins = {
        item["plan_id"]: item
        for item in fresh_checkins_result.data
    }

    completed = sum(1 for plan in plans if plan["id"] in fresh_checkins)

    st.metric("Today Progress", f"{completed}/{total}")

    progress = completed / total if total else 0
    st.progress(progress)

    st.divider()

    st.subheader("Today Details")

    rows = []
    for plan in plans:
        rows.append({
            "timing": plan["timing"],
            "supplement_name": plan["supplement_name"],
            "dosage": plan["dosage"],
            "frequency": plan["frequency"],
            "taken": plan["id"] in fresh_checkins,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
