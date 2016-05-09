import shelve
import pickle
import semidbm
from collections import defaultdict, namedtuple
from operator import itemgetter
from itertools import groupby
import string
import re

ReviewResult = namedtuple('ReviewResult', ['review_id', 'weight', 'text', 'stars', 'business', 'topics'])
Business = namedtuple('Business', ['business_id', 'url', 'name', 'categories', 'stars'])
BusinessResult = namedtuple('BusinessResult', ['business', 'pertinent_reviews'])

stopwords = set(['a', 'able', 'about', 'above', 'according', 'accordingly', 'across', 'actually', 'after', 'afterwards', 'again', 'against', 'all', 'allow', 'allows', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'an', 'and', 'another', 'any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart', 'appear', 'appreciate', 'appropriate', 'are', 'around', 'as', 'aside', 'ask', 'asking', 'associated', 'at', 'available', 'away', 'awfully', 'b', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beside', 'besides', 'best', 'better', 'between', 'beyond', 'both', 'brief', 'but', 'by', 'c', 'came', 'can', 'cannot', 'cant', 'cause', 'causes', 'certain', 'certainly', 'changes', 'clearly', 'co', 'com', 'come', 'comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains', 'corresponding', 'could', 'course', 'currently', 'd', 'definitely', 'described', 'despite', 'did', 'different', 'do', 'does', 'doing', 'done', 'down', 'downwards', 'during', 'e', 'each', 'edu', 'eg', 'eight', 'either', 'else', 'elsewhere', 'enough', 'entirely', 'especially', 'et', 'etc', 'even', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly', 'example', 'except', 'f', 'far', 'few', 'fifth', 'first', 'five', 'followed', 'following', 'follows', 'for', 'former', 'formerly', 'forth', 'four', 'from', 'further', 'furthermore', 'g', 'get', 'gets', 'getting', 'given', 'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'h', 'had', 'happens', 'hardly', 'has', 'have', 'having', 'he', 'hello', 'help', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'hi', 'him', 'himself', 'his', 'hither', 'hopefully', 'how', 'howbeit', 'however', 'i', 'ie', 'if', 'ignored', 'immediate', 'in', 'inasmuch', 'inc', 'indeed', 'indicate', 'indicated', 'indicates', 'inner', 'insofar', 'instead', 'into', 'inward', 'is', 'it', 'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kept', 'know', 'knows', 'known', 'l', 'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'like', 'liked', 'likely', 'little', 'look', 'looking', 'looks', 'ltd', 'm', 'mainly', 'many', 'may', 'maybe', 'me', 'mean', 'meanwhile', 'merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 'must', 'my', 'myself', 'n', 'name', 'namely', 'nd', 'near', 'nearly', 'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 'next', 'nine', 'no', 'nobody', 'non', 'none', 'noone', 'nor', 'normally', 'not', 'nothing', 'novel', 'now', 'nowhere', 'o', 'obviously', 'of', 'off', 'often', 'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall', 'own', 'p', 'particular', 'particularly', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 'presumably', 'probably', 'provides', 'q', 'que', 'quite', 'qv', 'r', 'rather', 'rd', 're', 'really', 'reasonably', 'regarding', 'regardless', 'regards', 'relatively', 'respectively', 'right', 's', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second', 'secondly', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious', 'seriously', 'seven', 'several', 'shall', 'she', 'should', 'since', 'six', 'so', 'some', 'somebody', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'still', 'sub', 'such', 'sup', 'sure', 't', 'take', 'taken', 'tell', 'tends', 'th', 'than', 'thank', 'thanks', 'thanx', 'that', 'thats', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'theres', 'thereupon', 'these', 'they', 'think', 'third', 'this', 'thorough', 'thoroughly', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together'
, 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying', 'twice', 'two', 'u', 'un', 'under', 'unfortunately', 'unless', 'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use', 'used', 'useful', 'uses', 'using', 'usually', 'uucp', 'v', 'value', 'various', 'very', 'via', 'viz', 'vs', 'w', 'want', 'wants', 'was', 'way', 'we', 'welcome', 'well', 'went', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'willing', 'wish', 'with', 'within', 'without', 'wonder', 'would', 'would', 'x', 'y', 'yes', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves', 'z', 'zero'])

tokenize_regex = re.compile(r'[a-z]+')

def to_url(business_name, city):
    x = (''.join([c for c in business_name.encode('utf-8') if 0 < ord(c) < 127])).replace('&', 'and').translate(None, string.punctuation).replace(' ', '-') + '-' + city.replace('-Baseline','')
    return x

weight_by_star = [0, # Should be no zero star ratings
                  0.5, # 1 star ratings, omit when possible
                  0.85, # 2 star ratings, should still be unlikely
                  1, # 3 star ratings, don't bias
                  1.2, # 4 star ratings, want to keep
                  1.5] # 5 star ratings are the best

CATEGORIES_WEIGHT = 1

class ReviewFinder:
    def __init__(self, city):
        self.city = city
        self.f = semidbm.open(city + '.db', flag='r')
        self.db = shelve.Shelf(self.f, protocol=pickle.HIGHEST_PROTOCOL)
    
    def __del__(self):
        self.f.close()
    
    def __review_list_for_term(self, term):
        try:
            return self.db["t=" + term][0]
        except KeyError:
            return []
        
    def __weight_for_term(self, term):
        try:
            #print(term+" score=" + str(1.0/len(self.db["t=" + term][0])))
            return 1.0/len(self.db["t=" + term][0])
        except KeyError:
            return 0
    
    def __review_list_for_topic(self, topic):
        try:
            return self.db["c=" + topic]
        except KeyError:
            return []
    
    def __business(self, business_id):
        name, categories, stars = self.db["b=" + business_id]
        return Business(business_id=business_id, url=to_url(name, self.city), name=name, categories=categories, stars=tuple([True] * int(stars) + [False] * (5-int(stars))))
    
    def __top_topics(self, review_id):
        results = []
        for topic, score in sorted(self.db["rt=" + review_id], key=itemgetter(1), reverse=True):
            _, (name, color) = self.db["c=" + str(topic)]
            if name != 'zzz':
              results.append((topic, name, color))
        return results
        
    def all_topics(self):
        topic = 1
        results = []
        while "c=" + str(topic) in self.db:
            _, (name, color) = self.db["c=" + str(topic)]
            if name != 'zzz':
                results.append((topic, name, color))
            topic+=1
        return results
        
    def find_reviews(self, keywords, limit):
        
        review_results = {}
        
        terms = tokenize_regex.findall(keywords.lower())
        for term in terms:
            if term not in stopwords:
                weight_for_term = self.__weight_for_term(term)
                for review, weight in self.__review_list_for_term(term):
                    if review not in review_results:
                        text, business_id, stars = self.db["r=" + review]
                        review_results[review] = (0.0, text, business_id, stars)
                    score, text, business_id, stars = review_results[review]
                    business_categories = self.db["b=" + business_id]
                    review_results[review] = ((score + weight * weight_by_star[stars] + CATEGORIES_WEIGHT * len([term for term in terms if term in business_categories])) / weight_for_term, text, business_id, stars)
        reviews = sorted(review_results.items(), key=lambda (review, props): props[0], reverse=True)[:limit]
        
        return [ReviewResult(review_id=review_id,
                             weight=props[0],
                             text=props[1],
                             stars=tuple([True] * props[3] + [False] * (5-props[3])),
                             business=self.__business(props[2]),
                             topics=self.__top_topics(review_id)[:5]) for review_id, props in review_results.items()]
    
    def find_more(self, review_id, query, limit, exclude_this_business):
        
        review_results = {}
        
        this_text, this_business_id, this_stars = self.db["r=" + review_id]
        terms = tokenize_regex.findall(query.lower())
        
        for topic, topic_weight in self.db["rt=" + review_id]:
            for review, review_weight in self.db["c=" + str(topic)][0]:
                if review not in review_results:
                    text, business_id, stars = self.db["r=" + review]
                    review_results[review] = (0.0, text, business_id, stars)
                score, text, business_id, stars = review_results[review]
                weight_for_terms_score = sum(self.__weight_for_term(term) for term in set(terms) & set(tokenize_regex.findall(text.lower())))

                review_results[review] = (score + topic_weight * review_weight * weight_by_star[stars] * (1 + 100*weight_for_terms_score), text, business_id, stars)
        
        reviews = sorted(review_results.items(), key=lambda (review, props): props[0], reverse=True)[:limit]
        
        results = [ReviewResult(review_id=review_id,
                                weight=0,
                                text=this_text,
                                stars=tuple([True] * this_stars + [False] * (5-this_stars)),
                                business=self.__business(this_business_id),
                                topics=self.__top_topics(review_id)[:5])]
        
        if exclude_this_business:
            results += [ReviewResult(review_id=review_id1,
                                     weight=props[0],
                                     text=props[1],
                                     stars=tuple([True] * props[3] + [False] * (5-props[3])),
                                     business=self.__business(props[2]),
                                     topics=self.__top_topics(review_id1)[:5]) for review_id1, props in reviews if this_business_id != props[2]]
        else:
            results += [ReviewResult(review_id=review_id1,
                                     weight=props[0],
                                     text=props[1],
                                     stars=tuple([True] * props[3] + [False] * (5-props[3])),
                                     business=self.__business(props[2]),
                                     topics=self.__top_topics(review_id1)[:5]) for review_id1, props in reviews if review_id1 != review_id]
       
        return results
    
    def find_by_topic(self, topic, limit):
        
        review_results = {}
        
        for review, review_weight in self.db["c=" + topic][0][:limit]:
            if review not in review_results:
                text, business_id, stars = self.db["r=" + review]
                review_results[review] = (0.0, text, business_id, stars)
            score, text, business_id, stars = review_results[review]
            review_results[review] = (score + review_weight * weight_by_star[stars], text, business_id, stars)
        
        return [ReviewResult(review_id=review_id,
                             weight=props[0],
                             text=props[1],
                             stars=tuple([True] * props[3] + [False] * (5-props[3])),
                             business=self.__business(props[2]),
                             topics=self.__top_topics(review_id)[:5]) for review_id, props in review_results.items()]
    
    def find_businesses(self, review_id, business_id, limit):
        this_business = self.__business(business_id)
        
        other_businesses = groupby([r for r in sorted(self.find_more(review_id, limit), key=itemgetter(4)) if r.business.business_id!=business_id], key=itemgetter(4))
        return [BusinessResult(business=this_business, pertinent_reviews=[])] + [BusinessResult(business=a[0], pertinent_reviews=list(a[1])) for a in other_businesses]

    def topic_name_by_id(self, topic_id):
      _, (name, color) = self.db["c=" + str(topic_id)]
      return name
