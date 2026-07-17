import json, os, time
from collections import deque
from threading import Lock

STORAGE_FILE = "deals_storage.json"
MAX_DEALS = 1000
lock = Lock()

def _load():
    if not os.path.exists(STORAGE_FILE):
        return {"posted_links": [], "deals": []}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f: 
            data = json.load(f)
        data["deals"] = deque(data.get("deals", []), maxlen=MAX_DEALS)
        return data
    except:
        return {"posted_links": [], "deals": deque(maxlen=MAX_DEALS)}

def _save(data):
    with lock:
        data["deals"] = list(data["deals"])
        with open(STORAGE_FILE, "w", encoding="utf-8") as f: 
            json.dump(data, f, ensure_ascii=False, indent=2)
        data["deals"] = deque(data["deals"], maxlen=MAX_DEALS)

def is_duplicate(url):
    data = _load()
    return url in data["posted_links"]

def add_deal(deal):
    data = _load()
    data["posted_links"].append(deal["source_url"])
    data["posted_links"] = data["posted_links"][-MAX_DEALS:]
    deal["posted_time"] = int(time.time())
    data["deals"].append(deal)
    _save(data)

def get_stats():
    data = _load()
    return {
        "total_posted": len(data["posted_links"]), 
        "last_deal": data["deals"][-1] if data["deals"] else None
    }