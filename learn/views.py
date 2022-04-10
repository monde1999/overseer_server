# from forecast.models import FloodProneArea, FloodLevel
import forecast.models as fmodels
from math import *

import requests
import json

from http import HTTPStatus
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import *

from . import z2

z2.run()

@api_view(['POST'])
def send_forecast(request):
    # print(request.data)
    forecast = int(request.data['forecast'])
    z2.forecast = forecast
    return Response(status=HTTPStatus.OK)

@api_view(['POST'])
def send_current(request):
    # print(request.data)
    cur_weather = int(request.data['cur_weather'])
    z2.weather = cur_weather
    # print("CURRENT WEATHER HAS CHANGED TO", cur_weather)
    return Response(status=HTTPStatus.OK)

@api_view(['POST'])
def send_car_position(request):
    # print(request.data)
    id = int(request.data['id'])
    latitude = float(request.data['latitude'])
    longitude = float(request.data['longitude'])
    user_loc = UserLocation(id,latitude,longitude)
    z2.user_locations.append(user_loc)
    return Response(status=HTTPStatus.OK)

@api_view(['POST'])
def send_flood_prone_area_location(request):
    # print(request.data)
    latitude = request.data['latitude']
    latitude = float(latitude)
    longitude = request.data['longitude']
    longitude = float(longitude)
    fpa = FloodProneArea(latitude,longitude,35)

    height = int(request.data['height']) # 1->4
    weather = int(request.data['weather']) # 200 -> light rain?
    # isFlooding? mausab to 
    # means dili siya kanavigate
    # retrieve function? sa csharp moretrieve sa flood level?
    # LetLeniLeadBBM 
    # 
    mult = get_mult(weather)

    #random
    #flood volume
    flood_start = int(request.data['flood_start'])
    flood_end = int(request.data['flood_end'])
    
    fh = int(height * mult)
    fh = max(fh,0)
    fl520 = FloodLevel(fpa,520,fh,flood_start,flood_end)
    mult *= 2
    fh = int(height * mult)
    fh = max(fh,0)
    fl200 = FloodLevel(fpa,200,fh,flood_start,flood_end)
    fl500 = FloodLevel(fpa,500,fh,flood_start,flood_end)
    fl521 = FloodLevel(fpa,521,fh,flood_start,flood_end)
    mult *= 2
    fh = int(height * mult)
    fh = max(fh,0)
    fl201 = FloodLevel(fpa,201,fh,flood_start,flood_end)
    fl501 = FloodLevel(fpa,501,fh,flood_start,flood_end)
    fl522 = FloodLevel(fpa,522,fh,flood_start,flood_end)
    mult *= 2
    fh = int(height * mult)
    fh = max(fh,0)
    fl202 = FloodLevel(fpa,202,fh,flood_start,flood_end)
    fl502 = FloodLevel(fpa,502,fh,flood_start,flood_end)
    mult *= 2
    fh = int(height * mult)
    fh = max(fh,0)
    fl503 = FloodLevel(fpa,503,fh,flood_start,flood_end)
    mult *= 2
    fh = int(height * mult)
    fh = max(fh,0)
    fl504 = FloodLevel(fpa,504,fh,flood_start,flood_end)

    fl531 = FloodLevel(fpa,531,0,flood_start,flood_end)

    fl = [fl520,fl200,fl500,fl521,
            fl201,fl501,fl522,fl202,fl502,
            fl503,fl504,fl531]

    z2.flood_prone_areas.append(fpa)
    z2.flood_levels.append([fpa,fl])
    print('=================FloodProneArea added========================')
    print('Base Weather:', weather)
    z2.print_iter('FloodProneArea FloodLevels', fl)
    print('=================END================================')
    
    #test analyzer
    # l = Location(latitude=latitude,longitude=longitude)
    # a = AffectedArea(location=l, weather=z2.weather, rain_start=0.0, flood_start=0.0, rain_end=9, flood_end=18)
    # m = Monitor(affected_area=a)
    # z2.analyzer.add_monitor(m)
    
    return Response(status=HTTPStatus.OK)

def get_mult(level):
    # intensities: lighter, light, moderate, heavy, very heavy
    mult = 0
    if level==520:
        mult = 1
    elif level==200 or level==500 or level==521:
        mult = 1/2
    elif level==201 or level==501 or level==522:
        mult = 1/4
    elif level==202 or level==502:
        mult = 1/8
    elif level==503:
        mult = 1/16
    elif level==504:
        mult = 1/32
    return mult

@api_view(['GET'])
def get_state(request):
    lat = request.query_params.get('latitude', None)
    lon = request.query_params.get('longitude', None)

    monitor = z2.analyzer.get_monitor(lat,lon)
    if monitor is not None:
        state = monitor.get_level()
        return Response(str(state))
    else:
        return Response('0')

@api_view(['POST'])
def send_area_state(request):
    lat = request.data['latitude']
    lon = request.data['longitude']
    state = request.data['state']
    level = request.data['level']
    if lat==None or lon==None or state==None or level==None:
        return Response(status=HTTPStatus.BAD_REQUEST)
    lat = int(lat)
    lon = int(lon)
    state = int(state)
    level = int(level)
    # print("REPORT {", lat, lon, state, "}")
    monitor = z2.analyzer.get_monitor(lat,lon)
    if monitor is not None:
        monitor.change_data_from_report(state, level)
    elif state==2 or state==3: # area is still not monitored
        w = z2.get_weather_current()
        if w!=0: 
            area = z2.get_flood_prone_area(lat,lon)
            loc = Location(lat,lon)
            rs = 0
            re = 18
            if state==3: re = 0
            fl = z2.get_flood_level(area,w)
            fs = fl.flood_start
            fe = fl.flood_end
            aarea = AffectedArea(loc,w,rs,re,fs,fe)
            z2.analyzer.add_monitor(Monitor(aarea))
            fl:FloodLevel
    return Response(status=HTTPStatus.OK)

##########################################################33

class Weather:
    def __init__(self, location, code):
        self.location = location
        self.code = code

class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

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
    areas = fmodels.FloodProneArea.objects.all()
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
            area = fmodels.FloodProneArea.objects.get(latitude=loc.latitude,longitude=loc.longitude)
            break
    return area

def determine_flood_start():
    return 60

def save_area(location, flood_level):
    area = get_area(location)
    if area is None:
        area = fmodels.FloodProneArea(latitude=location.latitude, longitude=location.longitude)
        area.save()
        LOCATIONS.append(location)
        
        rain_level = get_rain_level(location)
        flood_start = determine_flood_start() # to be edited
        fl = fmodels.FloodLevel(fpa=area, rain_level=rain_level, flood_level=flood_level, flood_start=flood_start)
        fl.save()
    return area

# LOCATIONS = []
LOCATIONS = get_locations()
WEATHER_LIST = [get_weather_list(LOCATIONS)]