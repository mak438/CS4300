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

with open(city + '.json') as reviews:
    reviews_list = json.load(reviews)
    for review in reviews_list:
        review_dict["r=" + str(review['review_id'])] = (review['text'], str(review['business_id']))
        
        for term in tokenize_regex.findall(review['text']):
            db["t=" + str(term)].append((str(term), 1))
            db["c=" + str(term)].append((str(review['review_id']), 1.0))

s = shelve.Shelf(semidbm.open(city + '-baseline.db', flag='n'), protocol=pickle.HIGHEST_PROTOCOL)
for k,v in db.items():
    s[k] = v
for k, v in review_dict.items():
    s[k] = v
s.close()