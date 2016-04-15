city = 'Urbana'

import os
import json
os.mkdir(city)

with open(city + '.json') as cityfile:
    reviews = json.load(cityfile)
    for review in reviews:
        with open(city + '/' + review['review_id'], 'w') as f:
            f.write(review['text'].encode('utf8'))
            
os.system("mallet-2.0.8RC3/bin/mallet import-dir --input " + city + " --output " + city + ".mallet --keep-sequence --remove-stopwords")