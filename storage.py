import json
import os

FILE_NAME = 'posted_deals.json'

def load_posted():
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, 'r') as f:
        return json.load(f)

def is_posted(link):
    posted = load_posted()
    return link in posted

def mark_posted(link):
    posted = load_posted()
    if link not in posted:
        posted.append(link)
        with open(FILE_NAME, 'w') as f:
            json.dump(posted, f)