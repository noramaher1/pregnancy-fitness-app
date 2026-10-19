import os
import time

import requests
from fastapi import FastAPI, Query

from rules import DISCLAIMER, RULES, trimester

WORKOUT_URL = os.environ.get("WORKOUT_URL", "http://workout-service:8000")
REDUCE_LOAD_MINUTES = int(os.environ.get("REDUCE_LOAD_MINUTES", "300"))
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
    tri = trimester(week)
    result = {
        "week": week,
        "trimester": tri,
        "exercises": RULES[tri]["do"],
        "avoid": RULES[tri]["avoid"],
        "weekly_minutes": None,
        "reduce_load": False,
        "notes": [],
        "disclaimer": DISCLAIMER,
    }
    minutes = fetch_weekly_minutes(user)
    if minutes is None:
        # Node Failure pattern: degrade to general advice instead of failing.
        result["notes"].append("Workout history is unavailable. Showing general advice only.")
        return result
    result["weekly_minutes"] = minutes
    if minutes > REDUCE_LOAD_MINUTES:
        result["reduce_load"] = True
        result["notes"].append(
            f"You logged {minutes} minutes in the last 7 days. Consider reducing intensity or duration."
        )
    return result
