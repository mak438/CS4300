city = 'Urbana'

import re
import pickle
import shelve
import semidbm
import pandas
from os.path import basename
from collections import defaultdict

tokenize_regex = re.compile(r'[A-Za-z0-9]+')

businesses = pandas.read_json('Business.json')
topics = pandas.melt(pandas.read_table('Urbana.topics.txt', header=None, names=['seq', 'review_id'] + range(1,100), index_col=False), id_vars=['seq', 'review_id'], var_name='topic', value_name='weight')
topics.review_id = topics.review_id.apply(basename)
wordweights = pandas.read_table('Urbana.wordweights.txt', header=None, names=['topic', 'term', 'weight'])
reviews = pandas.read_json('Urbana.json')

s = shelve.Shelf(semidbm.open(city + '.db', flag='n'), protocol=pickle.HIGHEST_PROTOCOL)

for b in businesses.itertuples():
    s["b=" + str(b.business_id)] = (b.name, b.categories, b.stars)
print("Written businesses")

categories = defaultdict(list)
for c in topics.itertuples():
    categories["c=" + str(c.topic)].append((c.review_id, c.weight))
for k,v in categories.items():
    s[k] = v
print("Written categories")

term_weights = defaultdict(list)
for t in wordweights.itertuples():
    term_weights["t=" + str(t.term)].append((t.topic, t.weight))
for k, v in term_weights.items():
    s[k] = v
print("Written terms")

for r in reviews.itertuples():
    s["r=" + str(r.review_id)] = (r.text, r.business_id, r.stars, r.date)
print("Written reviews")
s.close()