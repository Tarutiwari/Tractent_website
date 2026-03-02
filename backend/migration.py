"""
migration.py — MongoDB (PyMongo) version
Backfills missing 'status' field on existing tractor_bookings documents.
No ALTER TABLE needed — MongoDB is schema-less.
"""

from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")


def run_migration():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]

    # Backfill: add 'status' = 'Pending' to any bookings that are missing it
    result = db.tractor_bookings.update_many(
        {"status": {"$exists": False}},
        {"$set": {"status": "Pending"}}
    )
    print(f"[Migration] Backfilled 'status' field on {result.modified_count} booking document(s).")
    client.close()


if __name__ == "__main__":
    run_migration()
