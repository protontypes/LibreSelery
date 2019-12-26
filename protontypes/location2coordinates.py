from geopy.geocoders import Nominatim
from geopy.distance import geodesic

class LocationTransform
    def __init__(self):
        pass

    def Location2Coordiantes(location):
        geolocator = Nominatim(user_agent="protontypes")
        location = geolocator.geocode(location)
        return (location.latitude, location.longitude)

    def DistanceBetweenCoordiantes(start,destination):
        return geodesic(start,destination).km
