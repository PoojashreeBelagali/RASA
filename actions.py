from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet
import zomatopy
import mailsmyp
import json

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_restaurant'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"889129b59670ab646cf410cadfc1886b"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		cuisines_dict={'bakery':5,'chinese':25,'cafe':30,'italian':55,'biryani':7,'north indian':50,'south indian':85}
		results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 5)
		d = json.loads(results)
		response=""
		if d['results_found'] == 0:
			response= "no results"
		else:
			for restaurant in d['restaurants']:
				response=response+ "Found "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+"\n"
		
		dispatcher.utter_message("-----"+response)
		return [SlotSet('location',loc)]

class ActionSendMail(Action):
	def name(self):
		return 'action_mail'

	def run(self, dispatcher, tracker, domain):
		configZomato = {"user_key": "889129b59670ab646cf410cadfc1886b"}
		zomato = zomatopy.initialize_app(configZomato)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		location_detail = zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat = d1["location_suggestions"][0]["latitude"]
		lon = d1["location_suggestions"][0]["longitude"]
		cuisines_dict = {'bakery': 5, 'chinese': 25, 'cafe': 30, 'italian': 55, 'biryani': 7, 'north indian': 50,
						 'south indian': 85}
		results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 10)
		d = json.loads(results)
		response = ""
		if d['results_found'] == 0:
			response = "no results"
		else:
			for restaurant in d['restaurants']:
				response = response + "Found " + restaurant['restaurant']['name'] + " in " + \
						   restaurant['restaurant']['location']['address'] + "\n"

		config = {"user_mail": "kumarprakharbhagat.ml7@iiitb.net", "user_password": "Prakhar@1989"}
		mail = mailsmyp.initialize_app(config)
		to = tracker.get_slot('emailid')
		mail.send_mail(to, response)



