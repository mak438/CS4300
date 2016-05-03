from django.shortcuts import render_to_response

from find import ReviewFinder
from findbaseline import ReviewFinderBaseline

# Create your views here.
def reviews(request):
    city = request.GET.get('city')
    if city == 'Urbana-Baseline':
        f = ReviewFinderBaseline(city)
    else:
        f = ReviewFinder(city)
    return render_to_response('./reviews.html', {'city': city, 'reviews': f.find_reviews(str(request.GET.get('keywords')), 20), 'reviewtext': str(request.GET.get('keywords')) });

def reviewsByTopic(request):
    city = request.GET.get('city')
    if city == 'Urbana-Baseline':
        f = ReviewFinderBaseline(city)
    else:
        f = ReviewFinder(city)
    return render_to_response('./reviewsByTopic.html', {'city': city, 'reviews': f.find_by_topic(str(request.GET.get('topic')), 20), 'topic' : f.topic_name_by_id(request.GET.get('topic'))})

def moreReviews(request):
    city = request.GET.get('city')
    if city == 'Urbana-Baseline':
        f = ReviewFinderBaseline(city)
    else:
        f = ReviewFinder(city)
    return render_to_response('./moreReviews.html', {'city': city, 'reviews': f.find_more(str(request.GET.get('review_id')), 20), 'reviewtext': str(request.GET.get('reviewtext'))})

def home(request):
    f = ReviewFinder('Urbana')
    return render_to_response('./index.html', {'topics': f.all_topics()})

def showBusinesses(request):
    city = request.GET.get('city')
    if city == 'Urbana-Baseline':
        f = ReviewFinderBaseline(city)
    else:
        f = ReviewFinder(city)
    return render_to_response('./showBusinesses.html',{'city':city, 'businesses': f.find_businesses(str(request.GET.get('review_id')),str(request.GET.get('business_id')),20), 'reviewtext': str(request.GET.get('reviewtext'))})
