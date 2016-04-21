import shelve
import pickle
import semidbm
from collections import defaultdict, namedtuple
from operator import itemgetter
import string
import re

ReviewResult = namedtuple('ReviewResult', ['review_id', 'weight', 'text', 'date', 'stars', 'business'])
BusinessResult = namedtuple('BusinessResult', ['business_id', 'name', 'categories'])

tokenize_regex = re.compile(r'[A-Za-z]+')

def to_url(business_name, city):
    return business_name.replace('&', 'and').translate(None, string.punctuation).replace(' ', '-') + '-' + city.replace('-Baseline','')

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
    
    def __review_result(self, review):
        review_id, weight, stars, date = review
        text, business_id = self.db["r=" + review_id]
        return ReviewResult(review_id=review_id, weight=weight, text=text, stars=stars, date=date, business=self.business_review(business_id))
    
    def __business_review(self, business_id):
        name, categories = self.db["b=" + business_id]
        return BusinessResult(business_id=business_id, name=name, categories=categories)
    
    def find_reviews(self, keywords, limit=None):
        topics_by_weight = defaultdict(float)
        for term in tokenize_regex.findall(keywords):
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
        business_name = self.db["b=" + business_id]
        this_business = BusinessResult(business_id=to_url(business_name, self.city), business_name=business_name)
        return [this_business].extend(set([r.business for r in self.find_more(review_id, limit) if r.business.business_id!=business_id]))
