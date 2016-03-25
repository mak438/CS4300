import json
import guess_language


############Extract Businesses############
business = open('yelp_academic_dataset_business.json')
business_list = [json.loads(line) for line in business]

business_list = [b for b in business_list if 'Restaurants' in b['categories']]
business_ids = set([b['business_id'] for b in business_list])

businesses_to_save = [{'business_id': b['business_id'], 
						'name': b['name'], 
						'city': b['city'], 
						'state': b['state'], 
						'stars': b['stars'], 
						'categories': b['categories']} 
						for b in business_list]

print("Number of Restaurant businesses")
print(len(businesses_to_save))

print("Saving Businesses")
#Add to a json file
with open('Business.json', 'w') as outfile:
    json.dump(businesses_to_save, outfile)
print("Businesses saved")

###########Extract reviews###############
review = open('yelp_academic_dataset_review.json')
review_list = []

for r in review:
	rj = json.loads(r)
	if rj['business_id'] in business_ids:
		review_list.append(rj)

#########Filtering out non english reviews ##############
#########Saved for later############
#review_list_eng = [r for r in review_list if guess_language.guessLanguage(r['text'])=='en']

reviews_to_save = [{'business_id': r['business_id'], 
					'text': r['text'], 
					'review_id': r['review_id'], 
					'stars': r['stars']} 
					for r in review_list]

print("Number of Restaurant Reviews")
print(len(reviews_to_save))

print("Saving Reviews")
#Add to a json file
with open("Reviews.json","w") as outfile:
	json.dump(reviews_to_save, outfile)
print("Reviews saved")