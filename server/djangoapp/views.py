from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    if request.method == "GET":
        return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/anbind_djangoserver-space/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/anbind_djangoserver-space/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        context["review_list"] = reviews

        dealer_url = "https://us-east.functions.appdomain.cloud/api/v1/web/anbind_djangoserver-space/dealership-package/get-dealership"
        dealership = get_dealers_from_cf(dealer_url, id=dealer_id)
        context["dealership"] = dealership
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://us-east.functions.appdomain.cloud/api/v1/web/anbind_djangoserver-space/dealership-package/get-dealership"
        dealership = get_dealers_from_cf(dealer_url, id=dealer_id)
        context["dealership"] = dealership
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == "POST":
        print("POST")
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/anbind_djangoserver-space/dealership-package/post-review"
        review = {}
        review["name"] = request.user.username
        review["time"] = datetime.utcnow().isoformat()
        review["dealership"] = dealer_id
        review["review"] = request.POST['content']
        review["purchase_date"] = request.POST['purchasedate']
        review["purchase"] = False
        if 'purchasecheck' in request.POST:
            review["purchase"] = True
        car_id = request.POST["car"]
        car = CarModel.objects.get(pk=car_id)
        review["car_make"] = car.carmake.name
        review["car_model"] = car.name
        review["car_year"] = int(car.year.strftime("%Y"))

        json_payload = {}
        json_payload["review"] = review
        post_request(url, json_payload, dealerId=dealer_id)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
