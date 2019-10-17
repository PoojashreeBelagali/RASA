from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet
import zomatopy
import mailsmyp
import json
import base64

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
		city_name = d1["location_suggestions"][0]["name"]
		cuisines_dict = {'mexican': 73, 'chinese': 25, 'american': 1, 'italian': 55, 'north indian': 50,
						 'south indian': 85}
		city_set = {"bangalore", "chennai", "delhi", "hyderabad", "kolkata", "mumbai", "ahmedabad", "pune", "agra",
					"ajmer", "aligarh", "amravati", "amritsar", "asansol", "aurangabad", "bareilly", "belgaum",
					"bhavnagar", "bhiwandi", "bhopal", "bhubaneswar", "bikaner", "bilaspur", "bokarosteelcity",
					"chandigarh", "coimbatorenagpur", "cuttack", "dehradun", "dhanbad", "bhilai", "durgapur", "erode",
					"faridabad", "firozabad", "ghaziabad", "gorakhpur", "gulbarga", "guntur", "gwalior", "gurgaon",
					"guwahati", "hubli–dharwad", "indore", "jabalpur", "jaipur", "jalandhar", "jammu", "jamnagar",
					"jamshedpur", "jhansi", "jodhpur", "kakinada", "kannur", "kanpur", "kochi", "kottayam", "kolhapur",
					"kollam", "kota", "kozhikode", "kurnool", "ludhiana", "lucknow", "madurai", "malappuram", "mathura",
					"goa", "mangalore", "meerut", "moradabad", "mysore", "nanded", "nashik", "nellore", "noida",
					"palakkad", "patna", "pondicherry", "puruliaallahabad", "raipur", "rajkot", "rajahmundry", "ranchi",
					"rourkela", "salem", "sangli", "siliguri", "solapur", "srinagar", "thiruvananthapuram", "thrissur",
					"tiruchirappalli", "tirupati", "tirunelveli", "tiruppur", "tiruvannamalai", "ujjain", "bijapur",
					"vadodara", "varanasi", "vasai-virarcity", "vijayawada", "vellore", "warangal", "surat",
					"visakhapatnam"}

		isCityServiceable = city_name in city_set
		response = ""
		if isCityServiceable:
			results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 5)

			d = json.loads(results)

			if d['results_found'] == 0:
				response = "no results"
			else:
				for restaurant in d['restaurants']:
					response = response + restaurant['restaurant']['name'] + "	 in " + \
							   restaurant['restaurant']['location']['address'] + "has been rated" + \
							   restaurant['restaurant']['user_rating']['aggregate_rating'] + "\n"
		else :
			response = "Sorry this city is not serviceable"


		
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
		cuisines_dict = {'mexican': 73, 'chinese': 25, 'american': 1, 'italian': 55, 'north indian': 50,
						 'south indian': 85}
		results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 10)
		d = json.loads(results)
		response = "Hi There," + "\n\n" + "Please find the requested restaurant details" + "\n\n\n"
		if d['results_found'] == 0:
			response = "Sorry, no results found"
		else:
			for restaurant in d['restaurants']:
				response = response + restaurant['restaurant']['name'] + "	 in " + \
						   restaurant['restaurant']['location']['address'] + "has been rated" + \
						   restaurant['restaurant']['user_rating']['aggregate_rating'] + "\n"
		response = response + "\n\n" + "Best regards," + "\n" + "Foodie Inc."

		config = {"user_mail": "kumarprakharbhagat.ml7@iiitb.net", "user_password": base64.b64decode("UHJha2hhckAxOTg5")}
		mail = mailsmyp.initialize_app(config)
		to = tracker.get_slot('emailid')
		mail.send_mail(to, response)



