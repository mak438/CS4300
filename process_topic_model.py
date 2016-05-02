city = 'Urbana'

import re
import pickle
import shelve
import semidbm
import pandas
from os.path import basename
from collections import defaultdict
from math import sqrt

NUM_TOPICS = 40

tokenize_regex = re.compile(r'[A-Za-z]+')

s = shelve.Shelf(semidbm.open(city + '.db', flag='n'), protocol=pickle.HIGHEST_PROTOCOL)
for b in pandas.read_json('Business.json').itertuples():
    s["b=" + str(b.business_id)] = (b.name, b.categories, b.stars)

reviews_body = pandas.read_json('Urbana.json')

reviews_by_term = defaultdict(list)
for r in reviews_body.itertuples():
    for term in tokenize_regex.findall(r.text):
        reviews_by_term[term].append((r.review_id, 1))

for term, reviews in reviews_by_term.items():
    s["t=" + term] = reviews

topic_weights = pandas.read_table('Urbana.keys.txt', header=None, names=['topic', 'topic_weight'], usecols=[0,1])
topics = pandas.melt(pandas.read_table('Urbana.topics.txt', header=None, names=['seq', 'review_id'] + range(1,NUM_TOPICS), index_col=False), id_vars=['seq', 'review_id'], var_name='topic', value_name='weight')
topics.review_id = topics.review_id.apply(basename)
topics = topics.merge(topic_weights, on='topic')

topics_by_review = defaultdict(list)
reviews_by_topic = defaultdict(list)
for entry in topics.itertuples():
    topics_by_review[entry.review_id].append((entry.topic, entry.weight * sqrt(entry.topic_weight)))
    reviews_by_topic[entry.topic].append((entry.review_id, entry.weight * sqrt(entry.topic_weight)))
    
for review_id, topics in topics_by_review.items():
    s["rt=" + review_id] = topics
for review in reviews_body.itertuples():
    s["r=" + review.review_id] = (review.text, review.business_id, review.stars)
for topic, reviews in reviews_by_topic.items():
    s["c=" + str(topic)] = reviews

s.close()