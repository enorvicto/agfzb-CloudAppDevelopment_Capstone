import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    #api_key = kwargs.get("api_key")
    try:
        #if api_key:
        #    params = kwargs.get("params")
            # Basic authentication GET
        #    response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
        #                            auth=HTTPBasicAuth('apikey', api_key))            
        #    return response
        #else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs)
            json_data = json.loads(response.text)
            return json_data
    except:
        # If any error occurs
        print("Network exception occurred")
    #status_code = response.status_code
    #print("With status {} ".format(status_code))

# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    response = requests.post(url, params=kwargs, json=json_payload)
    return response


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    state = kwargs.get("state")
    id = kwargs.get("id")
    if state:
        json_result = get_request(url, state=state)
    elif id:
        json_result = get_request(url, id=id)
    else:
        json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            if "doc" in dealer:
                dealer_doc = dealer["doc"]
            else:
                dealer_doc = dealer
            asd = dealer_doc          
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"], st=dealer_doc["st"],
                                   state=dealer_doc["state"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    dealer_id = kwargs.get("dealer_id")
    json_result = get_request(url, dealership=dealer_id)
    
    if json_result:
        # Get the row list in JSON as reviews
        reviews = json_result["data"]["docs"]
        # For each dealer object
        for review in reviews:
            # Create a DealerReview object with values in `doc` object
            review_obj = DealerReview(dealership=review["dealership"], name=review["name"], purchase=review["purchase"], 
                                   review=review["review"], purchase_date=review["purchase_date"], car_make=review["car_make"],
                                   car_model=review["car_model"],
                                   car_year=review["car_year"], sentiment=analyze_review_sentiments(review["review"]), id=review["id"])
            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    url = "https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/eaaa8d2f-76c4-4160-97fc-8909667cd16e"
    api_key = "ON_LA0iDArpDFWX36CVUNgTtdmdUKhRPcRBW9PxaFzmB"    
    #params = dict()
    #params["text"] = text
    #params["version"] = "2022-04-07"
    #params["features"] = "sentiment"
    #params["return_analyzed_text"] = ""
    #sentiment_result = get_request(url, params=params, api_key=api_key)

    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url)

    response = natural_language_understanding.analyze(
        text=text,
        features=Features(sentiment=SentimentOptions(targets=[text])),
        return_analyzed_text=True).get_result()
    #res = response["sentiment"]["document"]["label"]
    #res = response["sentiment"]["targets"]["label"]
    #print(response["sentiment"]["document"]["label"])
    return response["sentiment"]["document"]["label"]


