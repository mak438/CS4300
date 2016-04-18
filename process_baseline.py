city = 'Urbana'

import collections
import pickle
import json
import re
import semidbm
import shelve

tokenize_regex = re.compile(r'[A-Za-z]+')

db = collections.defaultdict(list)
review_dict = {}

businesses_to_collect = set()

with open('Business.json') as f:
    businesses = {b['business_id'].encode('utf-8'): b['name'].encode('utf-8') for b in json.load(f)}

with open(city + '.json') as reviews:
    reviews_list = json.load(reviews)
    for review in reviews_list:
        review_dict["r=" + review['review_id'].encode('utf-8')] = (review['text'], review['business_id'].encode('utf-8'))
        
        for term in tokenize_regex.findall(review['text']):
            db["t=" + str(term)].append((term.encode('utf-8'), 1))
            db["c=" + str(term)].append((review['review_id'].encode('utf-8'), 1.0))
            businesses_to_collect.add(review['business_id'].encode('utf-8'))

s = shelve.Shelf(semidbm.open(city + '-baseline.db', flag='n'), protocol=pickle.HIGHEST_PROTOCOL)
for k,v in db.items():
    s[k] = v
for k, v in review_dict.items():
    s[k] = v
for b in businesses_to_collect:
    s["b=" + b] = businesses[b]
s.close()