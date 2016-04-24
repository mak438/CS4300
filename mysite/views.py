from django.shortcuts import render_to_response

from find import ReviewFinder

# Create your views here.
def reviews(request):
    city = request.GET.get('city')
    f = ReviewFinder(city)
    return render_to_response('./reviews.html', {'city': city, 'reviews': f.find_reviews(str(request.GET.get('keywords')), 20), 'reviewtext': str(request.GET.get('keywords')) });

def moreReviews(request):
    city = request.GET.get('city')
    f = ReviewFinder(city)
    return render_to_response('./moreReviews.html', {'city': city, 'reviews': f.find_more(str(request.GET.get('review_id')), 20), 'reviewtext': str(request.GET.get('reviewtext'))})

def home(request):
    return render_to_response('./index.html');

def showBusinesses(request):
	city = request.GET.get('city')
	f = ReviewFinder(city)
	return render_to_response('./showBusinesses.html',{'city':city, 'businesses': f.find_businesses(str(request.GET.get('review_id')),str(request.GET.get('business_id')),20), 'reviewtext': str(request.GET.get('reviewtext'))})
