import os
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

WORKOUT_URL = os.environ.get("WORKOUT_URL", "http://workout-service:8000")
RECOMMENDATION_URL = os.environ.get("RECOMMENDATION_URL", "http://recommendation-service:8000")
STATIC = Path(__file__).parent / "static"

app = FastAPI(title="Web gateway")


class WorkoutIn(BaseModel):
    user: str = Field(min_length=1, max_length=50)
    type: str = Field(min_length=1, max_length=50)
    minutes: int = Field(gt=0, le=600)
    week: int = Field(ge=1, le=42)


def call(method: str, base: str, path: str, **kwargs):
    try:
        r = requests.request(method, f"{base}{path}", timeout=5, **kwargs)
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Backend service unavailable")
    try:
        body = r.json()
    except ValueError:
        body = {}
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=body.get("detail", "Backend error"))
    return body


@app.get("/")
def landing():
    return FileResponse(STATIC / "index.html")


@app.get("/app")
def tracker():
    return FileResponse(STATIC / "app.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/api/overview")
def overview(user: str = Query(min_length=1, max_length=50), week: int = Query(ge=1, le=42)):
    """Aggregates both backends into one response for the browser."""
    workouts = call("GET", WORKOUT_URL, "/workouts", params={"user": user})
    try:
        rec = call("GET", RECOMMENDATION_URL, "/recommendations", params={"user": user, "week": week})
    except HTTPException:
        rec = None
    return {"workouts": workouts, "recommendation": rec}


@app.post("/api/workouts", status_code=201)
def add_workout(w: WorkoutIn):
    return call("POST", WORKOUT_URL, "/workouts", json=w.model_dump())


@app.delete("/api/workouts/{workout_id}")
def delete_workout(workout_id: str, user: str = Query(min_length=1, max_length=50)):
    return call("DELETE", WORKOUT_URL, f"/workouts/{workout_id}", params={"user": user})


@app.delete("/api/users/{user}")
def delete_user(user: str):
    return call("DELETE", WORKOUT_URL, f"/users/{user}")
