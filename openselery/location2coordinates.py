from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def Location2Coordiantes(location):
    geolocator = Nominatim(user_agent="openselery")
    location = geolocator.geocode(location)
    return (location.latitude, location.longitude)

def DistanceBetweenCoordiantes(start,destination):
    return geodesic(start,destination).km
