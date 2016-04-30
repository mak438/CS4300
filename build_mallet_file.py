city = 'Urbana'

import os
import re
import json

from stemming.porter2 import stem
os.mkdir(city)

tokenize_regex = re.compile(r'[A-Za-z]+')

with open(city + '.json') as cityfile:
    reviews = json.load(cityfile)
    for review in reviews:
        with open(city + '/' + review['review_id'], 'w') as f:
            f.write(tokenize_regex.sub(stem, review['text']))
            
os.system("mallet-2.0.8RC3/bin/mallet import-dir --input " + city + " --output " + city + ".mallet --keep-sequence --remove-stopwords")