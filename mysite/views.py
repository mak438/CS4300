from django.shortcuts import render_to_response

from find import ReviewFinder

# Create your views here.
def reviews(request):
    city = request.GET.get('city')
    f = ReviewFinder(city)
    return render_to_response('./reviews.html', {'city': city, 'reviews': f.find_reviews(str(request.GET.get('keywords')), 5)});

def more(request):
    city = request.GET.get('city')
    f = ReviewFinder(city)
    return render_to_response('./reviews.html', {'city': city, 'reviews': f.find_more(str(request.GET.get('review_id')), 5) })