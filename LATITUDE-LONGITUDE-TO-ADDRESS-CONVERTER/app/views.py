from django.shortcuts import render,redirect
from app.latLongToAddressConverter import AddressConverter

# Create your views here.
def index(request):
    if request.method == 'POST':
        lat = request.POST['lat']
        lon = request.POST['lon']

        addressConverter = AddressConverter()
        streetAddress = addressConverter.findAddress(lat, lon)
        context = {'streetAddress':streetAddress, 'lat':lat, 'lon':lon}
        return render(request,'app/index.html',context)

    else:
        return render(request,'app/index.html')
