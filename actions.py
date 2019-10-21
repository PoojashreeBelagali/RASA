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
        response = ""
        config = {"user_key": "c86b663aedfe8a2b54af34bfb337bb5c"}
        zomato = zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        price = tracker.get_slot('price')
        location_detail = zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        if len(d1["location_suggestions"]) == 0:
            dispatcher.utter_message('We do not operate in that area yet.')
            return [SlotSet('location', None)]
        lat = d1["location_suggestions"][0]["latitude"]
        lon = d1["location_suggestions"][0]["longitude"]
        city_name = str(d1["location_suggestions"][0]["city_name"]).lower()
        cuisines_dict = {'mexican': 73, 'chinese': 25, 'american': 1, 'italian': 55, 'north indian': 50,
                         'south indian': 85}
        city_set = {"bhubaneswar", "kolhapur", "mathura", "delhi ncr", "kanpur", "bhavnagar", "jammu", "delhi ncr",
                    "amravati", "gorakhpur", "vijayawada", "bokaro", "amritsar", "trichy", "kottayam", "srinagar",
                    "siliguri", "delhi ncr", "palakkad", "firozabad", "vadodara", "purulia", "trivandrum", "tirupati",
                    "durgapur", "lucknow", "ranchi", "bijapur", "varanasi", "bhopal", "allahabad", "patna",
                    "visakhapatnam", "dehradun", "nagpur", "mysore", "mumbai", "guntur", "dhanbad", "jhansi", "nanded",
                    "goa", "indore", "rajahmundry", "mumbai", "tiruvannamalai", "ludhiana", "kollam", "solapur",
                    "kozhikode", "vellore", "kurnool", "thrissur", "dharwad", "jalandhar", "meerut", "raipur",
                    "durg bhilai", "cuttack", "chennai", "moradabad", "bilaspur", "tirunelveli", "kannur", "bengaluru",
                    "kakinada", "surat", "belgaum", "hyderabad", "erode", "jabalpur", "pune", "rajkot", "agra",
                    "mangalore", "delhi ncr", "aligarh", "kota", "bhiwadi", "malappuram", "salem", "ahmedabad",
                    "nellore", "asansol", "warangal", "nashik", "coimbatore", "chennai", "aurangabad", "ajmer",
                    "gulbarga", "madurai", "chandigarh", "delhi ncr", "sangli", "jaipur", "guwahati", "ujjain",
                    "mumbai", "hubli", "bikaner", "bareilly", "kolkata", "jamshedpur", "rourkela", "jamnagar",
                    "jodhpur", "kochi", "gwalior", "tiruppur"}

        isCityServiceable = city_name in city_set

        if isCityServiceable and cuisine in cuisines_dict:
            response = self.findTopFive(lat, lon, str(cuisines_dict.get(cuisine)), price, zomato)
        elif not isCityServiceable:
            dispatcher.utter_message("We do not operate in that area yet.")
            return [SlotSet('location', None)]

        elif cuisine not in cuisines_dict:
            dispatcher.utter_message("Sorry this cuisine is not available")
            return [SlotSet('cuisine', None)]

        dispatcher.utter_message("-----\n" + response)
        return [SlotSet('location', loc)]


    def findTopFive(self, lat, lon, cusine, price, zomato):
        counter = 0
        offset = 0
        response = ""
        while True:
            results = zomato.restaurant_search("", lat, lon, cusine, offset)
            d = json.loads(results)
            if "code" not in d:
                if d['results_found'] == 0:
                    if counter == 0:
                        response = "Sorry, no results found"
                    break
                if price == "300":
                    filteredResult = [x for x in d['restaurants'] if x['restaurant']['average_cost_for_two'] <= 300]
                elif price == "300 to 700":
                    filteredResult = [x for x in d['restaurants'] if
                                      x['restaurant']['average_cost_for_two'] >= 300 and x['restaurant'][
                                          'average_cost_for_two'] <= 700]
                else:
                    filteredResult = [x for x in d['restaurants'] if x['restaurant']['average_cost_for_two'] >= 700]

                for restaurant in filteredResult:
                    if counter == 5:
                        break
                    response = response + "[" + restaurant['restaurant']['name'] + "] in [" + \
                               restaurant['restaurant']['location']['address'] + "] has been rated :" + \
                               restaurant['restaurant']['user_rating']['aggregate_rating'] + "\n"
                    counter = counter + 1

            if counter == 5:
                break
            if "code" in d:
                if counter != 0:
                    break
                else:
                    return "Sorry, server busy try after sometime."
            if offset == 500:
                if counter != 0:
                    break
                else:
                    return "No restaurants found, modify your search"
            offset = offset + 20
        return response


class ActionSendMail(Action):
    def name(self):
        return 'action_mail'

    def run(self, dispatcher, tracker, domain):
        configZomato = {"user_key": "c86b663aedfe8a2b54af34bfb337bb5c"}
        zomato = zomatopy.initialize_app(configZomato)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        price = tracker.get_slot('price')
        location_detail = zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat = d1["location_suggestions"][0]["latitude"]
        lon = d1["location_suggestions"][0]["longitude"]
        cuisines_dict = {'mexican': 73, 'chinese': 25, 'american': 1, 'italian': 55, 'north indian': 50,
                         'south indian': 85}

        if cuisine in cuisines_dict:
            response = self.findTopTen(lat, lon, str(cuisines_dict.get(cuisine)), price, zomato)
        elif cuisine not in cuisines_dict:
            response = "Sorry this cuisine is not available"

        config = {"user_mail": "kumarprakharbhagat.ml7@iiitb.net", "user_password": "Prakhar@1989"}
        mail = mailsmyp.initialize_app(config)
        to = tracker.get_slot('emailid')
        mail.send_mail(to, response)

    def findTopTen(self, lat, lon, cusine, price, zomato):
        counter = 0
        offset = 0
        response = "Hi There," + "\n\n" + "Please find the requested restaurant details" + "\n\n\n"
        while True:
            results = zomato.restaurant_search("", lat, lon, cusine, offset)
            d = json.loads(results)
            if "code" not in d:
                if d['results_found'] == 0:
                    if counter == 0:
                        response = "Sorry, no results found"
                    break
                if price == "300":
                    filteredResult = [x for x in d['restaurants'] if x['restaurant']['average_cost_for_two'] <= 300]
                elif price == "300 to 700":
                    filteredResult = [x for x in d['restaurants'] if
                                      x['restaurant']['average_cost_for_two'] >= 300 and x['restaurant'][
                                          'average_cost_for_two'] <= 700]
                else:
                    filteredResult = [x for x in d['restaurants'] if x['restaurant']['average_cost_for_two'] >= 700]

                for restaurant in filteredResult:
                    if counter == 10:
                        break
                    response = response + "Name: " + restaurant['restaurant']['name'] + "\nAddress: " + \
                               restaurant['restaurant']['location']['address'] + "\nRating: " + \
                               restaurant['restaurant']['user_rating']['aggregate_rating'] + \
                               "\nCost for two here is Rs." + str(
                        restaurant['restaurant']['average_cost_for_two']) + "\n\n"
                    counter = counter + 1

            if counter == 10:
                break
            if "code" in d:
                if counter != 0:
                    break
                else:
                    return "Sorry, server busy try after sometime."
            if offset == 500:
                if counter != 0:
                    break
                else:
                    return "No restaurants found, modify your search"
            offset = offset + 20

        response = response + "\n\n" + "Best regards," + "\n" + "Foodie Inc."

        return response
