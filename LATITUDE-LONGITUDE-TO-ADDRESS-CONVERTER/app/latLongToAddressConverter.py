from geopy.geocoders import Nominatim #for getting location from latitute and longitude

# initialisation
class AddressConverter:
    def __init__(self):
        pass

    def findAddress(self, lat, lon):
        geolocator = Nominatim(user_agent="App",timeout=100)
        location = None

        s = str(lat) + "," + str(lon)

        # Getting Street Address of the Location
        try:
            location = geolocator.reverse(s)
        except ValueError as e:
            return e

        if location == None:
            return "Location's Street Address Not Found!"
        else:
            strt = location.address
            return strt


