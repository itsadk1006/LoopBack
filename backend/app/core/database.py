import os
import json
import logging
from typing import List, Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger("loopback.database")

# Database State Globals
active_db_mode: str = "json_fallback"
mongo_client = None
mongo_db = None

SEED_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "seed_incidents.json"
)

def init_database() -> str:
    """
    Initializes database connection.
    Attempts MongoDB connection if MONGODB_URI is provided.
    Falls back to local JSON file storage if URI is absent or connection fails.
    """
    global active_db_mode, mongo_client, mongo_db

    if settings.MONGODB_URI:
        try:
            import pymongo
            client = pymongo.MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=2000)
            # Test ping
            client.admin.command('ping')
            mongo_client = client
            mongo_db = client[settings.MONGODB_DATABASE]
            active_db_mode = "mongodb"
            logger.info("Successfully connected to MongoDB server.")
            seed_database()
            return active_db_mode
        except Exception as e:
            logger.warning(f"MongoDB connection attempt failed ({e}). Falling back to local JSON database mode.")

    active_db_mode = "json_fallback"
    logger.info("Running in JSON file fallback database mode.")
    seed_database()
    return active_db_mode

def get_db_status() -> Dict[str, Any]:
    return {
        "mode": active_db_mode,
        "is_fallback": active_db_mode == "json_fallback",
        "database_name": settings.MONGODB_DATABASE if active_db_mode == "mongodb" else "seed_incidents.json"
    }

def _load_json_data() -> List[Dict[str, Any]]:
    if not os.path.exists(SEED_FILE_PATH):
        return []
    try:
        with open(SEED_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        logger.error(f"Error reading JSON seed file: {e}")
        return []

def _save_json_data(data: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(SEED_FILE_PATH), exist_ok=True)
    with open(SEED_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def seed_database() -> None:
    """Idempotently seeds baseline incidents if database is empty."""
    seed_data = _load_json_data()
    if not seed_data:
        return

    if active_db_mode == "mongodb" and mongo_db is not None:
        collection = mongo_db["incidents"]
        for item in seed_data:
            collection.update_one({"id": item["id"]}, {"$setOnInsert": item}, upsert=True)
        logger.info("Idempotent seed complete for MongoDB.")
    else:
        # For JSON fallback, ensure seed items exist
        existing = _load_json_data()
        existing_ids = {item["id"] for item in existing}
        updated = False
        for item in seed_data:
            if item["id"] not in existing_ids:
                existing.append(item)
                updated = True
        if updated or not existing:
            _save_json_data(existing if existing else seed_data)
        logger.info("Idempotent seed complete for JSON storage.")

def get_all_incidents() -> List[Dict[str, Any]]:
    if active_db_mode == "mongodb" and mongo_db is not None:
        collection = mongo_db["incidents"]
        records = list(collection.find({}, {"_id": 0}))
        return records
    return _load_json_data()

def get_incident_by_id(incident_id: str) -> Optional[Dict[str, Any]]:
    if active_db_mode == "mongodb" and mongo_db is not None:
        collection = mongo_db["incidents"]
        record = collection.find_one({"id": incident_id}, {"_id": 0})
        return record
    incidents = _load_json_data()
    for inc in incidents:
        if inc["id"] == incident_id:
            return inc
    return None

def save_incident(incident_data: Dict[str, Any]) -> None:
    incident_id = incident_data["id"]
    if active_db_mode == "mongodb" and mongo_db is not None:
        collection = mongo_db["incidents"]
        collection.update_one({"id": incident_id}, {"$set": incident_data}, upsert=True)
    else:
        incidents = _load_json_data()
        found = False
        for idx, inc in enumerate(incidents):
            if inc["id"] == incident_id:
                incidents[idx] = incident_data
                found = True
                break
        if not found:
            incidents.append(incident_data)
        _save_json_data(incidents)
