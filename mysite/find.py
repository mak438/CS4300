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

stopwords = set(['a', 'able', 'about', 'above', 'according', 'accordingly', 'across', 'actually', 'after', 'afterwards', 'again', 'against', 'all', 'allow', 'allows', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'an', 'and', 'another', 'any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart', 'appear', 'appreciate', 'appropriate', 'are', 'around', 'as', 'aside', 'ask', 'asking', 'associated', 'at', 'available', 'away', 'awfully', 'b', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beside', 'besides', 'best', 'better', 'between', 'beyond', 'both', 'brief', 'but', 'by', 'c', 'came', 'can', 'cannot', 'cant', 'cause', 'causes', 'certain', 'certainly', 'changes', 'clearly', 'co', 'com', 'come', 'comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains', 'corresponding', 'could', 'course', 'currently', 'd', 'definitely', 'described', 'despite', 'did', 'different', 'do', 'does', 'doing', 'done', 'down', 'downwards', 'during', 'e', 'each', 'edu', 'eg', 'eight', 'either', 'else', 'elsewhere', 'enough', 'entirely', 'especially', 'et', 'etc', 'even', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly', 'example', 'except', 'f', 'far', 'few', 'fifth', 'first', 'five', 'followed', 'following', 'follows', 'for', 'former', 'formerly', 'forth', 'four', 'from', 'further', 'furthermore', 'g', 'get', 'gets', 'getting', 'given', 'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'h', 'had', 'happens', 'hardly', 'has', 'have', 'having', 'he', 'hello', 'help', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'hi', 'him', 'himself', 'his', 'hither', 'hopefully', 'how', 'howbeit', 'however', 'i', 'ie', 'if', 'ignored', 'immediate', 'in', 'inasmuch', 'inc', 'indeed', 'indicate', 'indicated', 'indicates', 'inner', 'insofar', 'instead', 'into', 'inward', 'is', 'it', 'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kept', 'know', 'knows', 'known', 'l', 'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'like', 'liked', 'likely', 'little', 'look', 'looking', 'looks', 'ltd', 'm', 'mainly', 'many', 'may', 'maybe', 'me', 'mean', 'meanwhile', 'merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 'must', 'my', 'myself', 'n', 'name', 'namely', 'nd', 'near', 'nearly', 'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 'next', 'nine', 'no', 'nobody', 'non', 'none', 'noone', 'nor', 'normally', 'not', 'nothing', 'novel', 'now', 'nowhere', 'o', 'obviously', 'of', 'off', 'often', 'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall', 'own', 'p', 'particular', 'particularly', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 'presumably', 'probably', 'provides', 'q', 'que', 'quite', 'qv', 'r', 'rather', 'rd', 're', 'really', 'reasonably', 'regarding', 'regardless', 'regards', 'relatively', 'respectively', 'right', 's', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second', 'secondly', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious', 'seriously', 'seven', 'several', 'shall', 'she', 'should', 'since', 'six', 'so', 'some', 'somebody', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'still', 'sub', 'such', 'sup', 'sure', 't', 'take', 'taken', 'tell', 'tends', 'th', 'than', 'thank', 'thanks', 'thanx', 'that', 'thats', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'theres', 'thereupon', 'these', 'they', 'think', 'third', 'this', 'thorough', 'thoroughly', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together'
, 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying', 'twice', 'two', 'u', 'un', 'under', 'unfortunately', 'unless', 'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use', 'used', 'useful', 'uses', 'using', 'usually', 'uucp', 'v', 'value', 'various', 'very', 'via', 'viz', 'vs', 'w', 'want', 'wants', 'was', 'way', 'we', 'welcome', 'well', 'went', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'willing', 'wish', 'with', 'within', 'without', 'wonder', 'would', 'would', 'x', 'y', 'yes', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves', 'z', 'zero'])

tokenize_regex = re.compile(r'[a-z]+')

def to_url(business_name, city):
    x = (''.join([c for c in str(business_name) if 0 < ord(c) < 127])).replace('&', 'and').translate(None, string.punctuation).replace(' ', '-') + '-' + city.replace('-Baseline','')
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
            if term not in stopwords:
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