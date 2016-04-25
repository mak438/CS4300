import shelve
import pickle
import semidbm
from collections import defaultdict, namedtuple
from operator import itemgetter
from itertools import groupby
import string
import re

ReviewResult = namedtuple('ReviewResult', ['review_id', 'weight', 'text', 'date', 'stars', 'business'])
Business = namedtuple('Business', ['business_id', 'url', 'name', 'categories', 'stars'])
BusinessResult = namedtuple('BusinessResult', ['business', 'pertinent_reviews'])

tokenize_regex = re.compile(r'[a-z]+')

def to_url(business_name, city):
    x = (''.join([c for c in business_name if 0 < ord(c) < 127])).replace('&', 'and').translate(None, string.punctuation).replace(' ', '-') + '-' + city.replace('-Baseline','')
    return x
class ReviewFinder:
    def __init__(self, city):
        self.city = city
        self.f = semidbm.open(city + '.db', flag='r')
        self.db = shelve.Shelf(self.f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def __del__(self):
        self.f.close()
    
    def __topic_list_for_term(self, term):
        try:
            return self.db["t=" + term]
        except KeyError:
            return []
    
    def __review_list_for_topic(self, topic):
        try:
            return self.db["c=" + topic]
        except KeyError:
            return []
    
    def __review_result(self, review_id, weight):
        review = self.db["r=" + review_id]
        text, business_id, stars, date = review
        return ReviewResult(review_id=review_id, weight=weight, text=text, stars=tuple([True] * stars + [False] * (5-stars)), date=date, business=self.__business(business_id))
    
    def __business(self, business_id):
        name, categories, stars = self.db["b=" + business_id]
        return Business(business_id=business_id, url=to_url(name, self.city), name=name, categories=', '.join(categories), stars=tuple([True] * int(stars) + [False] * (5-int(stars))))

    def find_reviews(self, keywords, limit=None):
        topics_by_weight = defaultdict(float)
        for term in tokenize_regex.findall(keywords.lower()):
            for topic, weight in self.__topic_list_for_term(term):
                topics_by_weight[topic] += weight
        
        reviews_by_weight = defaultdict(float)
        for topic, topic_weight in topics_by_weight.items():
            for review, review_weight in self.__review_list_for_topic(str(topic)):
                reviews_by_weight[review] += topic_weight * review_weight
        
        reviews = sorted(reviews_by_weight.items(), key=itemgetter(1), reverse=True)
        if limit is not None:
            reviews = reviews[:limit]
        
        return [self.__review_result(r[0], r[1]) for r in reviews]
    
    def find_more(self, review_id, limit=None):
        review_text = self.db["r=" + review_id][0]
        print(len(review_text))
        return [review for review in self.find_reviews(review_text, limit) if review.review_id != review_id]
        
    def find_businesses(self, review_id, business_id, limit=None):
        this_business = self.__business(business_id)
        
        other_businesses = groupby([r for r in sorted(self.find_more(review_id, limit), key=itemgetter(5)) if r.business.business_id!=business_id], key=itemgetter(5))
        return [BusinessResult(business=this_business, pertinent_reviews=[])] + [BusinessResult(business=a[0], pertinent_reviews=list(a[1])) for a in other_businesses]