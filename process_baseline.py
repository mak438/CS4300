city = 'Urbana'

import collections
import pickle
import json
import re
import semidbm
import shelve

tokenize_regex = re.compile(r'[A-Za-z]+')

categories = collections.defaultdict(list)
review_dict = {}

terms_to_collect = set()
businesses_to_collect = set()

with open('Business.json') as f:
    businesses = {b['business_id'].encode('utf-8'): (b['name'].encode('utf-8'), [cat.encode('utf-8') for cat in b['categories'] if cat != 'Restaurants'], b['stars']) for b in json.load(f)}

with open(city + '.json') as reviews:
    reviews_list = json.load(reviews)
    for review in reviews_list:
        review_dict[review['review_id'].encode('utf-8')] = (review['text'].encode('utf-8'), review['business_id'].encode('utf-8'), review['stars'], review['date'].encode('utf-8'))
        
        for term in tokenize_regex.findall(review['text'].lower()):
            categories[term.encode('utf-8')].append((review['review_id'].encode('utf-8'), 1.0))
            terms_to_collect.add(term.encode('utf-8'))
            businesses_to_collect.add(review['business_id'].encode('utf-8'))

s = shelve.Shelf(semidbm.open(city + '-Baseline.db', flag='n'), protocol=pickle.HIGHEST_PROTOCOL)
for k,v in categories.items():
    s["c=" + k] = v
for k, v in review_dict.items():
    s["r=" + k] = v
for b in businesses_to_collect:
    s["b=" + b] = businesses[b]
for t in terms_to_collect:
    s["t=" + t] = [(t,1.0)]
s.close()