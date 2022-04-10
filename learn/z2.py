import schedule
import time
from threading import Thread

from .models import *

forecast = 0
weather = 0
user_locations = []
flood_prone_areas = []
flood_levels = []

forecaster = FloodForecaster()
analyzer = BehaviorAnalyzer()

# l = Location(latitude=100,longitude=100)
# a = AffectedArea(location=l, weather=0, rain_start=1.0, flood_start=1.5, rain_end=2.0, flood_end=2.5)
# m = Monitor(affected_area=a)
# analyzer.add_monitor(m)

# forecast every 30 * 100 ms and current
# forecast is equivalent to 30 minutes in original server
# schedules in original server
#
#
#
def get_unmonitored_fpa():
    res = []
    for fpa in flood_prone_areas:
        if not fpa.is_monitored:
            res.append(fpa)
    return res

def get_weather_current():
    return weather

def get_weather_forecast():
    return forecast

def get_flood_level(fpa,w):
    res = None
    found = False
    for fl in flood_levels:
        if fl[0] == fpa:
            for fl2 in fl[1]:
                if fl2.weather == w:
                    res = fl2
                    found=True
                    break
        if found:
            break
    return res

def get_flood_levels(fpa):
    res = []
    for fl in flood_levels:
        if fl[0] == fpa:
            res = fl[1]
    return res

def get_flood_prone_area(lat,lon):
    fpa = None
    for f in flood_prone_areas:
        if f.latitude == lat and f.longitude == lon:
            fpa = f
            break
    return fpa

def get_flood_level_v2(lat,lon,w):
    fpa = get_flood_prone_area(lat,lon)
    res = None
    found = False
    for fl in flood_levels:
        if fl[0] == fpa:
            for fl2 in fl[1]:
                if fl2.weather == w:
                    res = fl2
                    found=True
                    break
        if found:
            break
    return res



def flush_user_locations():
    user_locations.clear()

def print_iter(label, iterable):
    print(label + ":")
    for i in iterable:
        print("\t" + repr(i))

def run():
    thread = Thread(target=run_scheduled)
    thread.daemon = True
    thread.start()


def run_scheduled():
    schedule.every(0.1).seconds.do(t1)
    schedule.every(18).seconds.do(t2)
    schedule.every(3).seconds.do(t3)
    while True:
        schedule.run_pending()
        time.sleep(0.1)

def t1():
    # print('====================T1==========================')
    analyzer.flush()
    analyzer.run1()
    # print_iter('UserLocations', user_locations)
    analyzer.distribute_locations(user_locations)
    flush_user_locations()

def t2():
    print('====================T2==========================')
    print('Forecast:', forecast)
    print('Weather:', weather)
    forecaster.run()
    print_iter('Forecaster return', forecaster.affected_areas)
    analyzer.monitor_affected_areas(forecaster.affected_areas)
    print_iter('Monitored', analyzer.monitors)

def t3():
    analyzer.run2()
    # print(analyzer.monitors)
    print('====================T3==========================')

"""
    3 Threads:
        1. User Locations & Monitor (traffic analysis) -> every 10 seconds (0.1s)
            a. In Monitor:
                    a1. Move the next_user_locations to current_user_locations -> refreshMonitor()
                    a2. Basta something to do with fix_db(), get_traffic(), etc.
            b. Gather UserLocation
            c. BehaviorAnalyzer.distribute() -> put in next_user_locations
            d. Global.flush()
            e. Wait -> (a)
        2. Forecaster -> every 30 minute (18s)
            a. Iterate unmonitored FloodProneAreas if the areas are affected
            b. Save the affected areas in FloodForecaster.affected_areas
                Definition: Affected_Area - forecasted to be flooded
            c. Each added affected_area must call the function: BehaviorAnalyzer.add_monitor(Monitor())
            d. Wait -> (a)
        3. Monitor (weather update) -> check every 5 minutes (3s) [handled by BehaviorAnalyzer]
            a. Iterate the monitor object and check their current weather
            b. If the weather data in monitor is the same with the 
                current weather (means no change in weather) then do nothing,
            c. Else, execute the Monitor.intensity_change()
            d. Wait -> (a)
            
"""