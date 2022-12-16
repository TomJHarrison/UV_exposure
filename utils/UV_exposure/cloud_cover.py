import requests
import warnings

def get_cloud_mod_factor(lat, long, api_key):
    
    # Specify parameters required for API call
    params = {'access_key': api_key, 
              'query': str(lat) + ', ' + str(long)}

    # Make API request
    api_result = requests.get('http://api.weatherstack.com/current', params)
    api_response = api_result.json()

    # Extract cloud cover from API response
    cloud_cover = api_response['current']['cloudcover']

    # Depending on the level of cloud cover, the cloud modification factor changes
    # See equation 7 at the link below to see where the values below appear from:
    # https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2004RG000155
    if 0 <= cloud_cover < 2:
        cmf = 0.992
    elif 2 <= cloud_cover < 6:
        cmf = 0.896
    elif 6 <= cloud_cover < 9:
        cmf = 0.726
    else:
        cmf = 0.316
        
    return cmf