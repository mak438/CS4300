city = 'Urbana'

import re
import pickle
import shelve
import semidbm
import pandas
from os.path import basename
from collections import defaultdict

NUM_TOPICS = 40

tokenize_regex = re.compile(r'[A-Za-z]+')

def get_wordcounts():
    with open('Urbana.wordcounts.txt') as f:
        for line in f:
            parts = line.split()
            parts.pop(0)
            term = parts.pop(0)
            for wordcount in parts:
                topic, count = wordcount.split(":")
                yield {'term': term, 'topic': int(topic), 'count': int(count)}

wordcounts = pandas.DataFrame.from_dict(get_wordcounts())
wordcounts = wordcounts.merge(wordcounts[['topic', 'count']].groupby('topic').sum(), left_on='topic', right_index=True)

topic_weights = pandas.read_table('Urbana.keys.txt', header=None, names=['topic', 'topic_weight'], usecols=[0,1])

businesses = pandas.read_json('Business.json')
topics = pandas.melt(pandas.read_table('Urbana.topics.txt', header=None, names=['seq', 'review_id'] + range(1,NUM_TOPICS), index_col=False), id_vars=['seq', 'review_id'], var_name='topic', value_name='weight')
topics.review_id = topics.review_id.apply(basename)
reviews = pandas.read_json('Urbana.json')

weight_by_star = [0, # Should be no zero star ratings
                  0.5, # 1 star ratings, omit when possible
                  0.85, # 2 star ratings, should still be unlikely
                  1, # 3 star ratings, don't bias
                  1.2, # 4 star ratings, want to keep
                  1.5] # 5 star ratings are the best

topics = topics.merge(reviews, on='review_id')
topics = topics.merge(topic_weights, on='topic')

s = shelve.Shelf(semidbm.open(city + '.db', flag='n'), protocol=pickle.HIGHEST_PROTOCOL)

for b in businesses.itertuples():
    s["b=" + str(b.business_id)] = (b.name, b.categories, b.stars)
print("Written businesses")

categories = defaultdict(list)
for c in topics.itertuples():
    categories["c=" + str(c.topic)].append((c.review_id, c.weight * weight_by_star[c.stars] * c.topic_weight))
for k,v in categories.items():
    s[k] = v
print("Written categories")

term_weights = defaultdict(list)
for t in wordcounts.itertuples():
    term_weights["t=" + str(t.term)].append((t.topic, float(t.count_x) / t.count_y))
for k, v in term_weights.items():
    s[k] = v
print("Written terms")

for r in reviews.itertuples():
    s["r=" + str(r.review_id)] = (r.text, r.business_id, r.stars, r.date)
print("Written reviews")

s["num_topics"] = NUM_TOPICS

s.close()