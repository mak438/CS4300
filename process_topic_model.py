city = 'Urbana'

import collections
import shelve
import pickle
import json
import semidbm
from os.path import basename

db = collections.defaultdict(list)

businesses_to_collect = set()

with open('Business.json') as f:
    businesses = {b['business_id'].encode('utf-8'): b['name'].encode('utf-8') for b in json.load(f)}

with open(city + '.keys.txt') as keys:
    for row in keys:
        row = row.split()
        topic = row.pop(0)
        row.pop(0) # Ignore this
        for term in row:
            db["t=" + term].append((int(topic), 1))

with open(city + '.topics.txt') as topics:
    for row in topics:
        row = row.split()
        row.pop(0) # Ignore this
        review = basename(row.pop(0))
        while len(row)>0:
            topic = row.pop(0)
            weight = row.pop(0)
            db["c=" + topic].append((review, float(weight)))

with open(city + '.json') as reviews:
    reviews_list = json.load(reviews)
    for row in reviews_list:
        db["r=" + row['review_id'].encode('utf-8')] = (row['text'].encode('utf-8'), row['business_id'].encode('utf-8'))
        businesses_to_collect.add(row['business_id'].encode('utf-8'))

s = shelve.Shelf(semidbm.open(city + '.db', flag='n'), protocol=pickle.HIGHEST_PROTOCOL)
for k,v in db.items():
    s[k] = v
s.close()