import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pymongo import DESCENDING, MongoClient
from pymongo.errors import PyMongoError

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://workout-db:27017")
DB_NAME = os.environ.get("DB_NAME", "fitness")

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
workouts = client[DB_NAME]["workouts"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        workouts.create_index([("user", 1), ("created", DESCENDING)])
    except PyMongoError:
        pass  # database not up yet; the index is an optimisation only
    yield


app = FastAPI(title="Workout service", lifespan=lifespan)


class WorkoutIn(BaseModel):
    user: str = Field(min_length=1, max_length=50)
    type: str = Field(min_length=1, max_length=50)
    minutes: int = Field(gt=0, le=600)
    week: int = Field(ge=1, le=42)


def to_json(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "user": doc["user"],
        "type": doc["type"],
        "minutes": doc["minutes"],
        "week": doc["week"],
        "created": doc["created"].isoformat() + "Z",
    }


@app.exception_handler(PyMongoError)
async def db_unavailable(request, exc):
    # Busy Signal pattern: tell the caller to retry later.
    return JSONResponse(
        status_code=503,
        content={"detail": "Database unavailable"},
        headers={"Retry-After": "5"},
    )


@app.get("/health")
def health():
    """Liveness probe. Does not touch the database."""
    return {"status": "ok"}


@app.get("/ready")
def ready():
    """Readiness probe. Fails with 503 if MongoDB cannot be reached."""
    client.admin.command("ping")
    return {"status": "ready"}


@app.post("/workouts", status_code=201)
def add_workout(w: WorkoutIn):
    doc = {**w.model_dump(), "created": datetime.now(timezone.utc).replace(tzinfo=None)}
    result = workouts.insert_one(doc)
    return {"id": str(result.inserted_id)}


@app.get("/workouts")
def list_workouts(user: str = Query(min_length=1, max_length=50), limit: int = Query(50, ge=1, le=200)):
    cursor = workouts.find({"user": user}).sort("created", DESCENDING).limit(limit)
    return [to_json(d) for d in cursor]


@app.delete("/workouts/{workout_id}")
def delete_workout(workout_id: str, user: str = Query(min_length=1, max_length=50)):
    try:
        oid = ObjectId(workout_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid workout id")
    result = workouts.delete_one({"_id": oid, "user": user})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"deleted": 1}


@app.get("/stats")
def stats(user: str = Query(min_length=1, max_length=50), days: int = Query(7, ge=1, le=365)):
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    pipeline = [
        {"$match": {"user": user, "created": {"$gte": cutoff}}},
        {"$group": {"_id": None, "minutes": {"$sum": "$minutes"}, "count": {"$sum": 1}}},
    ]
    rows = list(workouts.aggregate(pipeline))
    if not rows:
        return {"user": user, "days": days, "minutes": 0, "count": 0}
    return {"user": user, "days": days, "minutes": rows[0]["minutes"], "count": rows[0]["count"]}


@app.delete("/users/{user}")
def delete_user_data(user: str):
    """Erasure endpoint for GDPR right to deletion."""
    result = workouts.delete_many({"user": user})
    return {"deleted": result.deleted_count}
