city = 'Urbana'

import collections
import shelve
import pickle
import json
from os.path import basename

db = collections.defaultdict(list)

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
        db["r=" + str(row['review_id'])] = (row['text'], str(row['business_id']))

s = shelve.open(city + '.db', flag='n', protocol=pickle.HIGHEST_PROTOCOL)
for k,v in db.items():
    s[k] = v
s.close()