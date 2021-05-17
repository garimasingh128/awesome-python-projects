from geopy.geocoders import Nominatim #for getting location from latitute and longitude
import pandas as pd #import to read csv

#initialisation
myfile = pd.read_csv("latlong2.csv",sep=",",usecols=['lat','lon'])
myfile =myfile.values.tolist()
geolocator = Nominatim(user_agent="App",timeout=100)


#convert list to string to import
s = str(myfile[0][0]) + "," + str(myfile[0][1])
street = []
address = []
for i in range(len(myfile)):
    #converting each row values to string
    s1 = str(myfile[i][0]) + "," + str(myfile[i][1])
    location = geolocator.reverse(s1)
    #getting address of location
    strt = location.address
    #getting address as dict
    address.append(location.raw['address'])
    street.append(strt)
print(street)