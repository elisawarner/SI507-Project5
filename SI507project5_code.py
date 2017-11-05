# Step 4 (400 points for code, 100 points for CSV files): Edit SI507project5_code.py as follows:

#Don't change the name of this file, though you may write other files and import them into this one.

#You must implement a caching system that ensures you will not run afoul of the rate limit of whatever API you use, and that you will not get data from the same request more than once per 12 hours, no matter how many times you run the program (at minimum. It could also be a week, 3 days, a month, whatever you want). HINT: Use the examples shown in class to implement functions that you can invoke to get and cache data from your API!

#You may want to consider writing functions that can generalize your code, so it is easy to write more code as you go on.

#You can borrow heavily from the code you saw in class, the examples on Canvas! But make sure these files you turn in run correctly and access the correct API (Tumblr, or Eventbrite).

#You must get data from this API that does require some method of authentication to access it -- OAuth1 or OAuth2 (some APIs have some endpoints that require OAuth and some that do not). The data must be enough data that your code written in this file, when run, results in CSV files, as follows...

#Your code must create at least 2 .CSV files of data with more than one column of data (e.g. one column of numbers 1, 2, 3, 4 ... and one column of names would not count. A spreadsheet provides numbers, you don't need Python for that). You may create more if you wish (e.g. Project 3 created 3 files) but you do not have to.

#Your code should pass all of your unit tests by the time you submit it, for full credit (but it should NOT pass all of your unit tests when there's no code in SI507project5_code.py yet, of course).

#There are no other requirements for your code in this project!

## import statements
import requests_oauthlib
import webbrowser
import json
import secret_data # need properly formatted file, see example
from datetime import datetime

## CACHING SETUP
##### CACHING SETUP #####
#--------------------------------------------------
# Caching constants
#--------------------------------------------------

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True
CACHE_FNAME = "cache_contents.json"
CREDS_CACHE_FILE = "creds.json"

#--------------------------------------------------
# Load cache files: data and credentials
#--------------------------------------------------
# Load data cache
try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}

# Load creds cache
try:
    with open(CREDS_CACHE_FILE,'r') as creds_file:
        cache_creds = creds_file.read()
        CREDS_DICTION = json.loads(cache_creds)
except:
    CREDS_DICTION = {}

#---------------------------------------------
# Cache functions
#---------------------------------------------
def has_cache_expired(timestamp_str, expire_in_days):
    """Check if cache timestamp is over expire_in_days old"""
    # gives current datetime
    now = datetime.now()

    # datetime.strptime converts a formatted string into datetime object
    cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

    # subtracting two datetime objects gives you a timedelta object
    delta = now - cache_timestamp
    delta_in_days = delta.days


    # now that we have days as integers, we can just use comparison
    # and decide if cache has expired or not
    if delta_in_days > expire_in_days:
        return True # It's been longer than expiry time
    else:
        return False

def get_from_cache(identifier, dictionary):
    """If unique identifier exists in specified cache dictionary and has not expired, return the data associated with it from the request, else return None"""
    identifier = identifier.upper() # Assuming none will differ with case sensitivity here
    if identifier in dictionary:
        data_assoc_dict = dictionary[identifier]
        if has_cache_expired(data_assoc_dict['timestamp'],data_assoc_dict["expire_in_days"]):
            if DEBUG:
                print("Cache has expired for {}".format(identifier))
            # also remove old copy from cache
            del dictionary[identifier]
            data = None
        else:
            data = dictionary[identifier]['values']
    else:
        data = None
    return data


def set_in_data_cache(identifier, data, expire_in_days):
    """Add identifier and its associated values (literal data) to the data cache dictionary, and save the whole dictionary to a file as json"""
    identifier = identifier.upper()
    CACHE_DICTION[identifier] = {
        'values': data,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CACHE_FNAME, 'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)

def set_in_creds_cache(identifier, data, expire_in_days):
    """Add identifier and its associated values (literal data) to the credentials cache dictionary, and save the whole dictionary to a file as json"""
    identifier = identifier.upper() # make unique
    CREDS_DICTION[identifier] = {
        'values': data,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CREDS_CACHE_FILE, 'w') as cache_file:
        cache_json = json.dumps(CREDS_DICTION)
        cache_file.write(cache_json)

#####

## ADDITIONAL CODE for program should go here...
## Perhaps authentication setup, functions to get and process data, a class definition... etc.

## OAuth1 API Constants - vary by API
### Private data in a hidden secret_data.py file
CLIENT_KEY = secret_data.client_key # what Twitter calls Consumer Key
CLIENT_SECRET = secret_data.client_secret # What Twitter calls Consumer Secret

### Specific to API URLs, not private
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
BASE_AUTH_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"


def get_tokens(client_key=CLIENT_KEY, client_secret=CLIENT_SECRET,request_token_url=REQUEST_TOKEN_URL,base_authorization_url=BASE_AUTH_URL,access_token_url=ACCESS_TOKEN_URL,verifier_auto=True):
    oauth_inst = requests_oauthlib.OAuth1Session(client_key,client_secret=client_secret)

    fetch_response = oauth_inst.fetch_request_token(request_token_url)

    # Using the dictionary .get method in these lines
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    auth_url = oauth_inst.authorization_url(base_authorization_url) #authorization_url is a method of requests_oathlib.OAuth1Session
    # Open the auth url in browser:
    # User input required
    webbrowser.open(auth_url) # For user to interact with & approve access of this app -- this script

    # Deal with required input, which will vary by API
    if verifier_auto: # if the input is default (True), like Twitter
        verifier = input("Please input the verifier:  ")
    else:
        redirect_result = input("Paste the full redirect URL here:  ")
        oauth_resp = oauth_inst.parse_authorization_response(redirect_result) # returns a dictionary -- you may want to inspect that this works and edit accordingly
        verifier = oauth_resp.get('oauth_verifier')

    # Regenerate instance of oauth1session class with more data
    oauth_inst = requests_oauthlib.OAuth1Session(client_key, client_secret=client_secret, resource_owner_key=resource_owner_key, resource_owner_secret=resource_owner_secret, verifier=verifier)

    oauth_tokens = oauth_inst.fetch_access_token(access_token_url) # returns a dictionary

    # Use that dictionary to get these things
    # Tuple assignment syntax
    resource_owner_key, resource_owner_secret = oauth_tokens.get('oauth_token'), oauth_tokens.get('oauth_token_secret')

    return client_key, client_secret, resource_owner_key, resource_owner_secret, verifier # returns authentication data

def get_tokens_from_service(service_name_ident, expire_in_days=7): # Default: 7 days for creds expiration
    creds_data = get_from_cache(service_name_ident, CREDS_DICTION) # loads from the cache important info for oauth
    if creds_data:
        if DEBUG:
            print("Loading creds from cache...")
            print()
    else:
        if DEBUG:
            print("Fetching fresh credentials...")
            print("Prepare to log in via browser.")
            print()
        creds_data = get_tokens() # function to get totally new authentication data
        set_in_creds_cache(service_name_ident, creds_data, expire_in_days=expire_in_days)
    return creds_data

def create_request_identifier(url, params_diction):
    sorted_params = sorted(params_diction.items(),key=lambda x:x[0])
    params_str = "_".join([str(e) for l in sorted_params for e in l]) # Make the list of tuples into a flat list using a complex list comprehension
    total_ident = url + "?" + params_str
    return total_ident.upper() # Creating the identifier

def get_data_from_api(request_url,service_ident, params_diction, expire_in_days=7):
    """Check in cache, if not found, load data, save in cache and then return that data"""
    ident = create_request_identifier(request_url, params_diction) # result identifier from create_request_identifier function
    data = get_from_cache(ident,CACHE_DICTION) # data returned from cache file with that identifier
    if data:
        if DEBUG:
            print("Loading from data cache: {}... data".format(ident))
    else:
        if DEBUG:
            print("Fetching new data from {}".format(request_url))

        # Get credentials
        client_key, client_secret, resource_owner_key, resource_owner_secret, verifier = get_tokens_from_service(service_ident) # tries to get from cache, else requests again

        # Create a new instance of oauth to make a request with
        oauth_inst = requests_oauthlib.OAuth1Session(client_key, client_secret=client_secret,resource_owner_key=resource_owner_key,resource_owner_secret=resource_owner_secret)
        # Call the get method on oauth instance
        # Work of encoding and "signing" the request happens behind the scenes, thanks to the OAuth1Session instance in oauth_inst
        resp = oauth_inst.get(request_url,params=params_diction) # actually request data from api
        # Get the string data and set it in the cache for next time
        data_str = resp.text
        data = json.loads(data_str)
        set_in_data_cache(ident, data, expire_in_days) # sets authentication info, actual data, and expiration here in cache
    return data

# Actually running API
if __name__ == "__main__":
    if not CLIENT_KEY or not CLIENT_SECRET:
        print("You need to fill in client_key and client_secret in the secret_data.py file.")
        exit()
    if not REQUEST_TOKEN_URL or not BASE_AUTH_URL:
        print("You need to fill in this API's specific OAuth2 URLs in this file.")
        exit()

    # Invoke functions
    twitter_search_baseurl = "https://api.twitter.com/1.1/search/tweets.json" # calling twitter api
    twitter_search_params = {'q':
    "University of Michigan", "count":4}

    twitter_result = get_data_from_api(twitter_search_baseurl,"Twitter",twitter_search_params) # Default expire_in_days
    print(type(twitter_result)) # searched twitter for U of M info



## Make sure to run your code and write CSV files by the end of the program.
