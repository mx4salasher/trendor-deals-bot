"""
storage.py
Lightweight JSON-file based storage — no external database needed.
Stores:
  - users.json  -> private-chat users who can receive broadcasts
  - deals.json  -> recent deals tagged by category, for deal-request auto-replies
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
DEALS_FILE = os.path.join(BASE_DIR, "deals.json")


def _load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_user(user_id: int, username: str = ""):
    users = _load(USERS_FILE, {})
    users[str(user_id)] = {"username": username, "joined": datetime.now().isoformat()}
    _save(USERS_FILE, users)


def get_all_user_ids():
    users = _load(USERS_FILE, {})
    return [int(uid) for uid in users.keys()]


def add_deal(title: str, affiliate_link: str, category: str):
    deals = _load(DEALS_FILE, [])
    deals.append({
        "title": title,
        "link": affiliate_link,
        "category": category.lower().strip(),
        "posted_at": datetime.now().isoformat(),
    })
    # keep only the most recent 200 deals to avoid unbounded growth
    deals = deals[-200:]
    _save(DEALS_FILE, deals)


def get_recent_deals_by_category(category: str, limit: int = 3):
    deals = _load(DEALS_FILE, [])
    matching = [d for d in deals if d["category"] == category.lower().strip()]
    return matching[-limit:][::-1]
