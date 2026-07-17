import json
import os
FILE = 'data.json'

def load():
    if not os.path.exists(FILE): return {"posted":[], "clicks":0, "earning":0}
    with open(FILE,'r') as f: return json.load(f)

def save(data):
    with open(FILE,'w') as f: json.dump(data,f)

def is_posted(link): return link in load()['posted']
def mark_posted(link):
    d=load(); d['posted'].append(link); save(d)
def add_click(link, amount=1):
    d=load(); d['clicks']+=1; d['earning']+=amount; save(d)
def get_stats():
    d=load(); return {"posted":len(d['posted']), "clicks":d['clicks'], "earning":d['earning']}