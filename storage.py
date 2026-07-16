"""
storage.py
Handles user and deal tracking (JSON based).
Now upgraded with stats and clean analytics retrieval!
"""
import os
import json
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
os.makedirs(DB_DIR, exist_ok=True)

USERS_FILE = os.path.join(DB_DIR, "users.json")
DEALS_FILE = os.path.join(DB_DIR, "deals.json")

def _load_json(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_user(user_id, username):
    users = _load_json(USERS_FILE)
    # Check if user already exists
    if not any(u["id"] == user_id for u in users):
        users.append({
            "id": user_id,
            "username": username,
            "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        _save_json(USERS_FILE, users)

def get_all_user_ids():
    users = _load_json(USERS_FILE)
    return [u["id"] for u in users]

def add_deal(title, affiliate_link, category, source_url=""):
    deals = _load_json(DEALS_FILE)
    deals.append({
        "title": title,
        "link": affiliate_link,
        "category": category,
        "source_url": source_url,
        "posted_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    _save_json(DEALS_FILE, deals)

def get_recent_deals_by_category(category, limit=3):
    deals = _load_json(DEALS_FILE)
    filtered = [d for d in deals if d.get("category", "").lower() == category.lower()]
    # Return latest first
    return sorted(filtered, key=lambda x: x.get("posted_time", ""), reverse=True)[:limit]

def get_last_deal():
    deals = _load_json(DEALS_FILE)
    if not deals:
        return None
    return sorted(deals, key=lambda x: x.get("posted_time", ""), reverse=True)[0]

def get_stats():
    deals = _load_json(DEALS_FILE)
    total_posted = len(deals)
    
    store_breakdown = {}
    for d in deals:
        url = d.get("source_url", "").lower()
        if "amazon" in url:
            store = "Amazon"
        elif "flipkart" in url:
            store = "Flipkart"
        else:
            store = "Other Store"
        store_breakdown[store] = store_breakdown.get(store, 0) + 1
        
    return {
        "total_posted": total_posted,
        "store_breakdown": store_breakdown
    }