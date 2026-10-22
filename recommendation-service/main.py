import os
import time
 
import requests
from fastapi import FastAPI, Query
 
from rules import (AVOID, DISCLAIMER, EXERCISES, SOURCES, STRENGTH_SESSIONS_PER_WEEK,
                   TIPS, WEEKLY_TARGET_MINUTES, stage_tips, trimester)
 
WORKOUT_URL = os.environ.get("WORKOUT_URL", "http://workout-service:8000")
# Stand-in for heavy recommendation logic. 0 means no extra work.
SIMULATE_CPU_MS = int(os.environ.get("SIMULATE_CPU_MS", "0"))
 
app = FastAPI(title="Recommendation service")
 
 
def burn_cpu(ms: int) -> None:
    """Keep one CPU core busy for about `ms` milliseconds."""
    end = time.perf_counter() + ms / 1000
    n = 0
    while time.perf_counter() < end:
        n += 1
 
 
@app.get("/health")
def health():
    return {"status": "ok"}
 
 
@app.get("/ready")
def ready():
    return {"status": "ready"}
 
 
def fetch_weekly_minutes(user: str):
    """Ask the workout service for the last 7 days. Retry once, then give up."""
    for _ in range(2):
        try:
            r = requests.get(f"{WORKOUT_URL}/stats", params={"user": user, "days": 7}, timeout=3)
            r.raise_for_status()
            return r.json()["minutes"]
        except (requests.RequestException, KeyError, ValueError):
            continue
    return None
 
 
@app.get("/recommendations")
def recommendations(
    week: int = Query(ge=1, le=42),
    user: str = Query(min_length=1, max_length=50),
):
    if SIMULATE_CPU_MS > 0:
        burn_cpu(SIMULATE_CPU_MS)
    result = {
        "week": week,
        "trimester": trimester(week),
        "exercises": [e["name"] for e in EXERCISES],
        "avoid": [a["name"] for a in AVOID],
        "tips": [t["text"] + " [" + t["source"] + "]" for t in TIPS + stage_tips(week)],
        "weekly_minutes": None,
        "weekly_target_minutes": WEEKLY_TARGET_MINUTES,
        "strength_sessions_per_week": STRENGTH_SESSIONS_PER_WEEK,
        "notes": [],
        "sources": SOURCES,
        "disclaimer": DISCLAIMER,
    }
    minutes = fetch_weekly_minutes(user)
    if minutes is None:
        # Node Failure pattern: degrade to general advice instead of failing.
        result["notes"].append("Workout history is unavailable. Showing general advice only.")
        return result
    result["weekly_minutes"] = minutes
    if minutes >= WEEKLY_TARGET_MINUTES:
        result["notes"].append(f"You logged {minutes} minutes in the last 7 days. You have reached the {WEEKLY_TARGET_MINUTES} minute weekly target.")
    else:
        result["notes"].append(
            f"You logged {minutes} of {WEEKLY_TARGET_MINUTES} target minutes in the last 7 days. "
            "Build up slowly, and any activity still helps."
        )
    return result
 