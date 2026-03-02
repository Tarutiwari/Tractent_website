"""
database.py — MongoDB version (PyMongo)
Collections:
  - users          : { email, username, password }
  - tractors       : { _id (ObjectId), email, tractor_model, location, price, photo, available }
  - tractor_bookings: { _id (ObjectId), tractor_id (str of ObjectId), email, delivery_location,
                        start_date, end_date, status }
  - user_profiles  : { email, address, contact_number, profile_photo }
"""

from dotenv import load_dotenv
import os
from pymongo import MongoClient
from bson import ObjectId
from passlib.context import CryptContext
from datetime import date

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "tractent")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- Connection ----------
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI)
        _db = _client[MONGO_DB_NAME]
    return _db

def init_db():
    """Create indexes for fast lookups."""
    db = get_db()
    db.users.create_index("email", unique=True)
    db.tractors.create_index("email")
    db.tractors.create_index("available")
    db.tractor_bookings.create_index("tractor_id")
    db.tractor_bookings.create_index("email")
    db.user_profiles.create_index("email", unique=True)
    print("[MongoDB] Indexes ensured.")


# ---------- Helper: convert ObjectId to str in a doc ----------
def _serialize(doc):
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ==================== USER ====================

def create_user(username: str, email: str, password: str):
    db = get_db()
    if db.users.find_one({"email": email}):
        return None
    hashed = pwd_context.hash(password)
    db.users.insert_one({"email": email, "username": username, "password": hashed})
    return get_user_by_email(email)


def get_user_by_email(email: str):
    db = get_db()
    return db.users.find_one({"email": email})


# ==================== TRACTOR ====================

def create_tractor(email: str, tractor_model: str, location: str,
                   price: float, photo: str = None):
    db = get_db()
    result = db.tractors.insert_one({
        "email": email,
        "tractor_model": tractor_model,
        "location": location,
        "price": price,
        "photo": photo,
        "available": True
    })
    tractor = db.tractors.find_one({"_id": result.inserted_id})
    return tractor_to_dict(tractor)


def get_all_tractors():
    db = get_db()
    return [tractor_to_dict(t) for t in db.tractors.find()]


def get_tractor_by_id(tractor_id: str):
    db = get_db()
    try:
        return db.tractors.find_one({"_id": ObjectId(tractor_id)})
    except Exception:
        return None


def set_tractor_availability(tractor_id: str, available: bool):
    db = get_db()
    db.tractors.update_one({"_id": ObjectId(tractor_id)}, {"$set": {"available": available}})


def tractor_to_dict(t):
    if t is None:
        return None
    return {
        "tractor_id": str(t["_id"]),
        "email": t.get("email"),
        "tractor_model": t.get("tractor_model"),
        "location": t.get("location"),
        "price": t.get("price"),
        "photo": t.get("photo"),
        "available": t.get("available", True),
    }


# ==================== BOOKING ====================

def create_booking(tractor_id: str, email: str, delivery_location: str,
                   start_date: date, end_date: date):
    db = get_db()
    result = db.tractor_bookings.insert_one({
        "tractor_id": tractor_id,
        "email": email,
        "delivery_location": delivery_location,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "status": "Pending"
    })
    return db.tractor_bookings.find_one({"_id": result.inserted_id})


def get_bookings_by_user(email: str):
    db = get_db()
    return list(db.tractor_bookings.find({"email": email}))


def get_booking_by_id(booking_id: str):
    db = get_db()
    try:
        return db.tractor_bookings.find_one({"_id": ObjectId(booking_id)})
    except Exception:
        return None


def update_booking_status(booking_id: str, status: str):
    db = get_db()
    db.tractor_bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": status}}
    )


def booking_to_dict(b, tractor=None):
    if b is None:
        return None
    return {
        "booking_id": str(b["_id"]),
        "tractor_id": b.get("tractor_id"),
        "email": b.get("email"),
        "delivery_location": b.get("delivery_location"),
        "start_date": b.get("start_date"),
        "end_date": b.get("end_date"),
        "status": b.get("status", "Pending"),
        "tractor": tractor
    }


def get_pending_bookings_for_owner(owner_email: str):
    """Return all Pending bookings for tractors owned by owner_email."""
    db = get_db()
    owner_tractors = list(db.tractors.find({"email": owner_email}, {"_id": 1}))
    tractor_ids = [str(t["_id"]) for t in owner_tractors]
    return list(db.tractor_bookings.find({
        "tractor_id": {"$in": tractor_ids},
        "status": "Pending"
    }))


# ==================== USER PROFILE ====================

def create_or_update_profile(email, address=None, contact=None, photo=None):
    db = get_db()
    existing = db.user_profiles.find_one({"email": email})
    update_fields = {}
    if address is not None:
        update_fields["address"] = address
    if contact is not None:
        update_fields["contact_number"] = contact
    if photo is not None:
        update_fields["profile_photo"] = photo

    if existing:
        if update_fields:
            db.user_profiles.update_one({"email": email}, {"$set": update_fields})
    else:
        db.user_profiles.insert_one({
            "email": email,
            "address": address,
            "contact_number": contact,
            "profile_photo": photo
        })
    return db.user_profiles.find_one({"email": email})


def profile_to_dict(p):
    if p is None:
        return None
    return {
        "email": p.get("email"),
        "address": p.get("address"),
        "contact_number": p.get("contact_number"),
        "profile_photo": p.get("profile_photo")
    }