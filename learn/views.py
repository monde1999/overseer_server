from forecast.models import FloodProneArea, FloodLevel
from math import *

import requests
import json

# class FloodForecaster:
#     def __init__(self):
#         self.areas = None
#         self.affectedAreas = None

class Weather:
    def __init__(self, location, code):
        self.location = location
        self.code = code

class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

# class Area:
#     def __init__(self):
#         self.location = None
#         self.table_of_flood_level = None

# class FloodLevel:
#     def __init__(self):
#         self.rain_level = None
#         self.flood_level = None
#         self.flood_start = None

def distance(location1, location2):
    """
        Returns distance of two geographic coordinates in meters.
        The formula is from the spherical law.
    """
    lat1 = location1.latitude
    long1 = location1.longitude
    lat2 = location2.latitude
    long2 = location2.longitude
    return acos(cos(radians(90-lat1)) * cos(radians(90-lat2)) + sin(radians(90-lat1)) * sin(radians(90-lat2)) * cos(radians(long1-long2))) * 6371000

def get_locations():
    areas = FloodProneArea.objects.all()
    locations = []
    for area in areas:
        loc = Location(area.latitude, area.longitude)
        locations.append(loc)
    return locations

def get_rain_level(location):
    # url = 'http://api.openweathermap.org/data/2.5/weather'
    # url += '?lat=' + str(location.latitude) + '&lon=' + str(location.longitude)
    # url += '&appid=67aa636d02df1df62ef01de2db58fa49'
    # r = requests.get(url)
    # data = json.loads(r.content.decode())
    # w_id = data['weather'][0]['id']
    # return w_id
    return 200

def get_weather_list(locations):
    weather_list = []
    for loc in locations:
        weather_list.append(get_rain_level(loc))
    return weather_list

def get_area(location):
    area = None
    for loc in LOCATIONS:
        d = distance(location, loc)
        if d <= 100: #100 meters
            area = FloodProneArea.objects.get(latitude=loc.latitude,longitude=loc.longitude)
            break
    return area

def determine_flood_start():
    return 60

def save_area(location, flood_level):
    area = get_area(location)
    if area is None:
        area = FloodProneArea(latitude=location.latitude, longitude=location.longitude)
        area.save()
        LOCATIONS.append(location)
        
        rain_level = get_rain_level(location)
        flood_start = determine_flood_start() # to be edited
        fl = FloodLevel(fpa=area, rain_level=rain_level, flood_level=flood_level, flood_start=flood_start)
        fl.save()
    return area

LOCATIONS = get_locations()
WEATHER_LIST = [get_weather_list(LOCATIONS)]