import shelve
import pickle
from collections import defaultdict, namedtuple
from operator import itemgetter

ReviewResult = namedtuple('ReviewResult', ['review_id', 'weight', 'text', 'business_id'])

class ReviewFinder:
    def __init__(self, city):
        self.db = shelve.open(city + '.db', protocol=pickle.HIGHEST_PROTOCOL)
    
    def __del__(self):
        self.db.close()
    
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
        return ReviewResult(review_id=review_id, weight=weight, text=review[0], business_id=review[1])
    
    def find_reviews(self, terms, limit=None):
        topics_by_weight = defaultdict(float)
        for term in terms:
            for topic, weight in self.__topic_list_for_term(term):
                topics_by_weight[topic] += weight
        
        reviews_by_weight = defaultdict(float)
        for topic, topic_weight in topics_by_weight.items():
            for review, review_weight in self.__review_list_for_topic(topic):
                reviews_by_weight[review] += topic_weight * review_weight
        
        reviews = sorted(reviews_by_weight.items(), key=itemgetter(1), reverse=True)
        if limit is not None:
            reviews = reviews[:limit]
        
        return [self.__review_result(r[0], r[1]) for r in reviews]