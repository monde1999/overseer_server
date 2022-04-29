from math import *
import requests
import json
import datetime
from . import z2
class Location():
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
    
    def __repr__(self):
        return 'Location[%d,%d]' % (self.latitude, self.longitude)

class UserLocation(Location):
    def __init__(self, id, latitude, longitude):
        super(UserLocation, self).__init__(latitude,longitude)
        self.id = id
    def __repr__(self):
        return "UserLocation[ID[%d],Location[%d,%d]]" % (self.id, self.latitude, self.longitude)


class FloodProneArea():
    def __init__(self, latitude, longitude, radius):
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
        self.is_monitored = False
    def __repr__(self):
        return 'FloodProneArea[Location[%d,%d],Monitored[%s]]' % (self.latitude, self.longitude, self.is_monitored)

class FloodLevel():
    def __init__(self, fpa, weather, level, flood_start, flood_end):
        self.fpa = fpa
        self.weather = weather
        self.level = level
        self.flood_start = flood_start
        self.flood_end = flood_end
        self.flood_n = 0 # +1 end sa monitor
        self.level_n = 0 # +1 every report
    def __repr__(self):
        return 'FloodLevel[%s,Weather[%d],Level[%d],FS[%0.1f],FE[%0.1f],FN[%d],LN[%d]]' % \
            (self.fpa,self.weather,self.level,self.flood_start,self.flood_end,self.flood_n,self.level_n)

class AffectedArea():
    def __init__(self, location, weather,rain_start, rain_end, flood_start, flood_end):
        self.location = location
        self.weather = weather
        self.rain_start = rain_start
        self.rain_end = rain_end
        self.flood_start = flood_start
        self.flood_end = flood_end

    def __repr__(self):
        return 'AffectedArea[%s,Weather[%d],RS[%0.1f],FS[%0.1f],RE[%0.1f],FE[%0.1f]]' % \
            (self.location,self.weather,self.rain_start,self.flood_start,self.rain_end,self.flood_end)

class FloodForecaster:
    API_KEY = ''

    def __init__(self):
        self.locations = []
        self.w_log = []
        # self.flood_level = FloodLevel.objects.all()
        self.affected_areas = []

    def run(self):
        print('Getting locations...')
        self.get_locations()
        z2.print_iter('Unmonitored FPAs', self.locations)

        print('Getting forecasts...')
        self.get_locations_weather()
        z2.print_iter('FPAs Weather Forecasts', ['%s --> %d' % (key,value) for key, value in self.w_log[0].items()])

        print('Forecasting floods...')
        self.get_affected_areas()
        z2.print_iter('Forecasted to Flood', self.affected_areas)

    def get_locations(self): # only get unmonitored locations # to update
        # areas = FloodProneArea.objects.filter(is_monitored=False)
        areas = z2.get_unmonitored_fpa()
        locations = []
        for area in areas:
            loc = Location(area.latitude, area.longitude)
            locations.append(loc)
        self.locations = locations
    
    # def get_weather(self, location):   # to check, get weather 30 minutes ahead
        # weather.dequeue??
        # url = 'http://api.openweathermap.org/data/2.5/weather'
        # url += '?lat=' + str(location.latitude) + '&lon=' + str(location.longitude)
        # url += '&appid=' + self.API_KEY
        # r = requests.get(url)
        # data = json.loads(r.content.decode())
        # w_id = data['weather'][0]['id']
        # return w_id

    def get_locations_weather(self):
        w_list = dict()
        for loc in self.locations:
            # w = self.get_weather(loc)
            w = z2.get_weather_forecast()
            w_list[loc] = w
        self.w_log.insert(0,w_list)
        if len(self.w_log) > 24:
            self.w_log.pop()

    def is_affected(self, loc, w):
        lat = loc.latitude
        lon = loc.longitude
        # fl = self.flood_level.filter(fpa__latitude=lat, fpa__longitude=lon,rain_level=w)
        fl = z2.get_flood_level_v2(lat,lon,w)
        if fl is None or fl.level==0:
            return False, None
        else:
            return True, fl
        
    def get_affected_areas(self):
        affected_areas = [] # AffectedArea instances
        for loc, w in self.w_log[0].items():
            # loc = w_item.key()
            # w = w_item.value()
            res = self.is_affected(loc,w)
            if res[0] == True:
                # rs = datetime.datetime.now() + datetime.timedelta(minutes=30)
                # rs = datetime.datetime.now() + datetime.timedelta(seconds=18)
                rs = 18
                # re = rs + datetime.timedelta(minutes=30)  #find when rain stops
                # re = rs + datetime.timedelta(seconds=18)
                re = 18
                # fs = rs + datetime.timedelta(minutes=res[1].flood_start)
                # fs = rs + datetime.timedelta(seconds=res[1].flood_start)
                fs = res[1].flood_start
                fh = res[1].level
                # fe = re + datetime.timedelta(minutes=res[1].flood_end)
                # fe = re + datetime.timedelta(seconds=res[1].flood_end)
                fe = res[1].flood_end
                affected_areas.append(AffectedArea(loc,w,rs,re,fs,fe))
        self.affected_areas = affected_areas

class Monitor:
    def __init__(self, affected_area):
        self.area = affected_area
        self.square_radius = 10 # default
        self.user_locations_current={}
        self.user_locations_previous={}
        self.user_locations_next={}
        self.to_destroy = False
        self.time_instantiated = datetime.datetime.now()
    
    def __repr__(self):
        s = 'Monitor[%s,Destroy[%s],Inst[%s]]' % (self.area, self.to_destroy, self.time_instantiated)
        s += '\nTLevel[' + str(self.get_traffic()) + ']'
        return s
    
    # def info(self):
    #     return 'Monitor[%s]' % self.area

    def print_next_locations(self):
        print('Next User Locations')
        for key in self.user_locations_next:
            print('ID: ',self.user_locations_next[key].id, 'Location: ', self.user_locations_next[key])
        print('------------------------------------------------------')
    
    def refreshMonitor(self):
        self.user_locations_previous = self.user_locations_current
        self.user_locations_current = self.user_locations_next
        self.user_locations_next = {}
    
    def get_level(self):
        base_time = self.time_instantiated
        current_time = datetime.datetime.now()
        res = 0
        """
            0 - waiting
            1 - rain_started
            2 - flood_started
            3 - flood_ending
            4 - flood_ended; monitor to be destroyed

            |----------> rain_start ---------------> flood_start ----------------> rain_end --------------> flood_end ------------|
             waiting(0)             rain_started(1)              flood_started(2)           flood_ending(3)           destroying(4)
        """
        base_time = base_time + datetime.timedelta(seconds = self.area.rain_start)
        if current_time >= base_time: res+=1   
        base_time = base_time + datetime.timedelta(seconds = self.area.flood_start)
        if current_time >= base_time: res+=1
        base_time = base_time + datetime.timedelta(seconds = self.area.rain_end)
        if current_time >= base_time: res+=1
        base_time = base_time + datetime.timedelta(seconds = self.area.flood_end)
        if current_time >= base_time: res+=1
        # print("INFO: get_level() ->", res)
        return res

    
    def addLocation(self,user_id,location):
        self.user_locations_next[user_id] = location
    
    def get_traffic(self):
        vehicle_count = 0
        moving_count = 0
        distance_threshold = 3 # to be changed
        movement_threshold = .7
        # for all elements in current_locs
        # if same user id exists in previous, increment vehicle count, get distance
        # if distance > threshold increment moving_count
        # return moving_count / vehicle_count >= .7 

        for k, v in self.user_locations_current.items():
            prev_location = self.user_locations_previous.get(k)
            if prev_location!=None:
                vehicle_count+=1
            else: continue
            if self.getDistance(prev_location, v) >= distance_threshold:
                moving_count+=1
        # return (moving_count / vehicle_count) >= movement_threshold
        if vehicle_count==0: return 1
        else: return moving_count / vehicle_count
        '''
            explanation:
                - naay traffic kung 70% nag move
                - ang wla nag-move pasabot na stuck, kay di man maggamit ang user sa app kung wla sya nag nav.
        '''
    
    def getDistance(self, location1,location2):
        lat1Rad = location1.latitude * pi / 180
        lat2Rad = location2.latitude * pi / 180
        R = 6371e3
        latDiffRad = (location2.latitude - location1.latitude) * pi /180
        lonDiffRad = (location2.longitude - location1.longitude) * pi / 180
        a = sin(latDiffRad/2)**2 + cos(lat1Rad) * cos(lat2Rad) * sin(lonDiffRad/2)**2
        c = 2 * atan2(a**0.5, (1-a)**0.5)
        return R * c 

    """
        0 - waiting
        1 - rain_started
        2 - flood_started
        3 - flood_ending
        4 - flood_ended; monitor to be destroyed

          no_rain                 with_rain                    with_rain                  no_rain
        |----------> rain_start ---------------> flood_start ----------------> rain_end --------------> flood_end ------------|
          waiting(0)             rain_started(1)              flood_started(2)           flood_ending(3)           destroying(4)
    """

    def weather_update(self, current_w_id):
        forecast_w_id = self.area.weather
        lvl = self.get_level()
        if forecast_w_id == current_w_id:
            if lvl==0: 
                print('\t[UPDATE] Rain starts earlier. Starting rain...')
                self.start_rain() # happens when the rain starts earlier
            elif lvl>=3: 
                print('\t[UPDATE] Rain is longer than expected. Extending rain...')
                self.extend_rain() # happens when the rain is longer than expected
        else:
            if self.has_rain(current_w_id): 
                print('\t[UPDATE] Weather changed. Changing monitor values...')
                self.intensity_change(current_w_id) # happens when weather changes
            else: # no rain
                if lvl==1: 
                    print('\t[UPDATE] Rain did not start as expected. Extending rain wait...')
                    self.extend_wait() # happens when rain does not start than expected
                elif lvl==2: 
                    print('\t[UPDATE] Rain stopped earlier. Ending rain...')
                    self.end_rain() # happens when rains stops earlier
                elif lvl==4: 
                    print('\t[UPDATE] Monitor stopped. Updating the database...')
                    self.wait_and_fix_db()

    def has_rain(self, w_id):
        w_rain = [200, 201, 202, 500, 501, 502, 503, 504, 520, 521, 522, 531]
        return w_id in w_rain

    def start_rain(self):
        self.area.rain_start = self.seconds_between(datetime.datetime.now(), self.time_instantiated)

    def extend_rain(self):
        # self.area.rain_end += datetime.timedelta(minutes = 5)
        self.area.rain_end += 3 # 3 seconds == 5minutes

    def intensity_change(self, current_w_id):
        loc = self.area.location
        # area = FloodProneArea.object.get(latitude=loc.latitude, longitude=loc.longitude)
        # fl = FloodLevel.objects.get(fpa=area, weather=current_w_id)
        fl = self.area
        self.area.weather = current_w_id
        self.area.flood_start = fl.flood_start
        self.area.flood_end = fl.flood_end
    
    def extend_wait(self):
        # self.area.rain_start += datetime.timedelta(minutes = 5)
        self.area.rain_start += 3 # 3 seconds == 5 minutes

    def end_rain(self):
        # total_seconds = self.area.rain_start + self.area.flood_start + self.area.rain_end
        # rain_end_datetime = self.time_instantiated  + datetime.timedelta(seconds=total_seconds)
        # self.area.rain_end = self.seconds_between(datetime.datetime.now(), self.time_instantiated)
        total_seconds = self.area.rain_start + self.area.flood_start
        flood_start_datetime = self.time_instantiated  + datetime.timedelta(seconds=total_seconds)
        self.area.rain_end = self.seconds_between(datetime.datetime.now(), flood_start_datetime)
        
        """
            0 - waiting
            1 - rain_started
            2 - flood_started
            3 - flood_ending
            4 - flood_ended; monitor to be destroyed

            no_rain                 with_rain                    with_rain                  no_rain
            |----------> rain_start ---------------> flood_start ----------------> rain_end --------------> flood_end ------------|
            waiting(0)             rain_started(1)              flood_started(2)           flood_ending(3)           destroying(4)
        """

        """
            [AR] Check the level of traffic. Range: 0 to 1
            - 0 to 0.1 -> stuck
            - 0.9 to 1 -> free
            2. [AR] If the traffic level is free and monitor is still not destroyed: (wla na nag baha)
            - destroy the monitor
            - change the flood end in db by ((current_time - rain_end)+flood_end)//2
            3. [AR] If the traffic level is stuck and monitor timer ends: (nagbaha pa)
            - flag the monitor with: WAITING
            - wait until the traffic level is free and fix the flood end in db by ((current_time - rain_end)+flood_end)//2
            4. [AR] If traffic is undefined (no vehicle), wait the monitor to stop. Don't fix the db.
        """
          
    def wait_and_fix_db(self):
        traffic = self.get_traffic()
        if traffic >= 0.9:
            print('Traffic level is ' + str(traffic) + '. Saving monitor data to db.')
            # fix db
            loc = self.area.location
            w_id = self.area.weather
            # area = FloodProneArea.objects.get(latitude=loc.latitude, longitude=loc.longitude)
            # obj = FloodLevel.objects.get(fpa=area, rain_level=w_id)
            area = z2.get_flood_prone_area(loc.latitude,loc.longitude)
            obj = z2.get_flood_level(area,w_id)
            # ave1 = (obj.flood_start * obj.flood_start_n + self.area.flood_start)//(obj.flood_start_n+1)
            x = obj.flood_n
            ave1 = (obj.flood_start * x + self.area.flood_start) // (x+1)
            obj.flood_start = ave1
            # obj.flood_start_n += 1
            # ave2 = (obj.flood_end * obj.flood_end_n + self.area.flood_end)//(obj.flood_end_n+1)
            ave2 = (obj.flood_end * x + self.area.flood_end) // (x+1)
            obj.flood_end = ave2
            # obj.flood_end_n += 1
            print("++++++++++NEW DATA+++++++++++++")
            fl = z2.get_flood_levels(area)
            z2.print_iter("FloodProneArea FloodLevels", fl)

            obj.flood_n += 1
            area.is_monitored = False
            # area.save()
            # obj.save()
            self.to_destroy = True
        else: # extend the flood
            print('Traffic level is' + str(traffic) + '. Extending flood.')
            # self.area.flood_end += datetime.timedelta(minutes=5)
            self.area.flood_end += 3

    def seconds_between(self, d1, d2):
        return abs((d2 - d1).total_seconds())
    
    def change_data_from_report(self, state, level):
        # lvl = self.get_level()
        # if lvl< 2:
        #     #flood_start -> pila ka minutes mo start ang flood after ni rain
        #     # m = self.minutes_between(datetime.datetime.now(), self.time_instantiated)
        #     m = self.seconds_between(datetime.datetime.now(), self.time_instantiated)
        #     self.area.flood_start = m - self.area.rain_start
        #     '''
        #     if sa system wla pa nag ulan (rain_start), negative ang result sa taas
        #     '''                 
        # else: do nothing
        """
            0 - waiting
            1 - rain_started
            2 - flood_started
            3 - flood_ending
            4 - flood_ended; monitor to be destroyed

            no_rain                 with_rain                    with_rain                  no_rain
            |----------> rain_start ---------------> flood_start ----------------> rain_end --------------> flood_end ------------|
            waiting(0)             rain_started(1)              flood_started(2)           flood_ending(3)           destroying(4)
        """
        # print("+++++++++++++REPORT CAPTURED++++++++++++++")
        if state==2:
            fl:FloodLevel = z2.get_flood_level_v2(
                self.area.location.latitude,
                self.area.location.longitude,
                self.area.weather
            )
            x = fl.level_n
            fl.level = (fl.level * x + level) // (x+1)
            fl.level_n += 1

            lvl = self.get_level()
            if lvl==2 or lvl==3: return
            elif lvl==0: # monitor just started
                print('>>> [REPORT] A flood is reported but lvl is 0. Starting flood...')
                self.start_flood(0)
            elif lvl==1: # monitor is marked raining but not flooded
                print('>>> [REPORT] A flood is reported but lvl is 1. Starting flood...')
                self.start_flood(1)
            # elif lvl==3: # monitor is flood ending
            #     print('>>> [REPORT] A flood is reported but lvl is 3. Extending flood...')
                # self.extend_flood()
            elif lvl==4 and self.to_destroy: # monitor is to be destroyed
                print('>>> [REPORT] A flood is reported but lvl is 4. Making new Monitor...')
                # monitor = Monitor(self.area)
                # monitor.area.weather = z2.get_weather_current()
                # monitor.area.flood_end += 3
                # monitor.time_instantiated = self.time_instantiated
                # z2.analyzer.add_monitor(monitor)
                self.to_destroy = False
                self.area.flood_end += 3
        elif state==1:
            lvl = self.get_level()
            if lvl==2 or lvl==3:
                print('>>> [REPORT] A false flood is reported but lvl is 2 or 3. Changing flood_start...')
                now = datetime.datetime.now()
                seconds = self.seconds_between(self.time_instantiated, now)
                seconds -= self.area.rain_start
                self.area.flood_start += 3
        elif state==3:
            lvl = self.get_level()
            if lvl==4:
                print('>>> [REPORT] A flood is reported after rain but lvl is 4. Changing flood_end...')
                self.to_destroy = False
                self.area.flood_end += 3
        elif state==0:
            lvl = self.get_level()
            if lvl==3:
                print('>>> [REPORT] A false flood is reported but lvl is 3. Changing flood_end...')
                self.area.flood_end -= 3

    def extend_flood(self):
        self.area.flood_end += 3

    def start_flood(self, lvl):
        if lvl==0:
            self.area.rain_start = 0
            self.area.flood_start = self.seconds_between(datetime.datetime.now(),self.time_instantiated)
        elif lvl==1:
            flood_start_datetime = self.time_instantiated + datetime.timedelta(seconds=self.area.rain_start)
            self.area.flood_start = self.seconds_between(datetime.datetime.now(),flood_start_datetime)
        

class BehaviorAnalyzer:
    def __init__(self) -> None:
        self.monitors = []
        """
            0 - waiting_to_rain_start
            1 - rain_start_started
            2 - flood_start_started
            3 - rain_end_started
            4 - flood_end_started
            5 - flood_ended; monitor to be destroyed
        """
    
    def get_monitor(self, lat, lon):
        res = None
        for monitor in self.monitors:
            lat0 = monitor.area.location.latitude
            lon0 = monitor.area.location.longitude
            if lat==lat0 and lon==lon0:
                res = monitor
                break
        return res

    def monitor_affected_areas(self, affected_areas):
        for area in affected_areas:
            self.add_monitor(Monitor(area))
        
    def add_monitor(self, monitor):
        self.monitors.append(monitor)
        loc:Location = monitor.area.location
        fpa:FloodProneArea = z2.get_flood_prone_area(loc.latitude,loc.longitude)
        fpa.is_monitored=True
        # fpa = FloodProneArea.objects.get(latitude=loc.latitude, longitude=loc.longitude)
        # fpa.is_monitored = True
        # fpa.save()

    def run1(self): # to be run every 10 seconds
        self.refresh_monitors()

    def run2(self): # to be ran every 5 minutes
        self.get_weather_update()

    def refresh_monitors(self): # update
        for monitor in self.monitors:
            # if monitor.get_level() > 1:
            monitor.refreshMonitor()

    # API_KEY = '67aa636d02df1df62ef01de2db58fa49'
    def get_weather(self, location):
        url = 'http://api.openweathermap.org/data/2.5/weather'
        url += '?lat=' + str(location.latitude) + '&lon=' + str(location.longitude)
        url += '&appid=67aa636d02df1df62ef01de2db58fa49'
        r = requests.get(url)
        data = json.loads(r.content.decode())
        w_id = data['weather'][0]['id']
        return w_id

        # 0 -> default
        # 1 -> current_time >= rain_start and 
        
    # def get_weather_sim(self):
    #     return z2.get_weather_current()
    
    def get_weather_update(self):  # every 5 minutes
        print('Getting weather update...')
        for monitor in self.monitors:
            # lvl = monitor.get_level()
            # if lvl==0 or lvl==1 or lvl==2:
            print('\tchecking %s...' % monitor)
            # loc = monitor.area.location
            # forecast_w_id = monitor.area.weather
            current_w_id = z2.get_weather_current()
            monitor.weather_update(current_w_id)
        print('Weather update ended.')

        """
            0 - waiting
            1 - rain_started
            2 - flood_started
            3 - flood_ending
            4 - flood_ended; monitor to be destroyed

            no_rain                 with_rain                    with_rain                  no_rain
            |----------> rain_start ---------------> flood_start ----------------> rain_end --------------> flood_end ------------|
            waiting(0)             rain_started(1)              flood_started(2)           flood_ending(3)           destroying(4)
        """
        
    def flush(self):
        self.monitors = [monitor for monitor in self.monitors if monitor.to_destroy == False]
    
    def distribute_locations(self, locations):
        for loc in locations:
            for monitor in self.monitors:
                m_loc = monitor.area.location
                if self.distance(m_loc, loc)<=35:
                    monitor.addLocation(loc.id,loc)
                    # print('Car %d added.' % loc.id)
                    break
    
    def distance(self, location1, location2):
        """
            Returns distance of two geographic coordinates in meters.
            The formula is from the spherical law.
        """
        lat1 = location1.latitude
        long1 = location1.longitude
        lat2 = location2.latitude
        long2 = location2.longitude
        return ((lat1-lat2)**2 + (long1-long2)**2)**0.5

    def get_monitor(self, latitude, longitude):
        res = None
        for monitor in self.monitors:
            loc = monitor.area.location
            lat = loc.latitude
            lon = loc.longitude
            if lat==latitude and lon==longitude:
                res = monitor
                break
        return res