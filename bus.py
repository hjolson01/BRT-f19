from math import sin, cos, asin, sqrt, pi
import pandas as pd
from zipfile import ZipFile
from datetime import datetime
from time import time
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import statistics as stat

def haversine_miles(lat1, lon1, lat2, lon2):
    """Calculates the distance between two points on earth using the
    harversine distance (distance between points on a sphere)
    See: https://en.wikipedia.org/wiki/Haversine_formula

    :param lat1: latitude of point 1
    :param lon1: longitude of point 1
    :param lat2: latitude of point 2
    :param lon2: longitude of point 2
    :return: distance in miles between points
    """
    lat1, lon1, lat2, lon2 = (a/180*pi for a in [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon/2) ** 2
    c = 2 * asin(min(1, sqrt(a)))
    d = 3956 * c
    return d


class Location:
    """Location class to convert lat/lon pairs to
    flat earth projection centered around capitol
    """
    capital_lat = 43.074683
    capital_lon = -89.384261

    def __init__(self, latlon=None, xy=None):
        if xy is not None:
            self.x, self.y = xy
        else:
            # If no latitude/longitude pair is given, use the capitol's
            if latlon is None:
                latlon = (Location.capital_lat, Location.capital_lon)

            # Calculate the x and y distance from the capital
            self.x = haversine_miles(Location.capital_lat, Location.capital_lon,
                                     Location.capital_lat, latlon[1])
            self.y = haversine_miles(Location.capital_lat, Location.capital_lon,
                                     latlon[0], Location.capital_lon)

            # Flip the sign of the x/y coordinates based on location
            if latlon[1] < Location.capital_lon:
                self.x *= -1

            if latlon[0] < Location.capital_lat:
                self.y *= -1

    def dist(self, other):
        """Calculate straight line distance between self and other"""
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __repr__(self):
        return "Location(xy=(%0.2f, %0.2f))" % (self.x, self.y)

class Trip: 
    '''A trip is like a row in a timetable for a particular route. 
    Buses may run many trips per day in service of, say, route 80 in Madison.'''

    def __init__(self, trip_id=None, route_id=None, bikes_allowed=None):
        self.trip_id = trip_id 
        self.route_id = route_id
        self.bikes_allowed = bikes_allowed


    def __repr__(self):
        return 'Trip({}, {}, {})'.format(repr(self.trip_id), repr(self.route_id), repr(self.bikes_allowed))

class BusDay:
    '''An object of type BusDay desribes the bus trips and
    routes available in Madison for a specific day''' 

    def __init__(self, date=None, service_ids=None, weekday=None, root=None, stops=None):
        
        
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("calendar.txt") as f:
                df_bus = pd.read_csv(f)
                self.weekday = date.isoweekday()
                self.date = date.strftime('%Y%m%d')
        df_fri = df_bus[df_bus['friday'] == 1]
        df_sat = df_bus[df_bus['saturday'] == 1]
        if self.weekday == 5 and self.date <= '20200301':
            df_fri = pd.DataFrame(df_fri[df_fri['start_date']<20200301])
            list_fri = list(df_fri['service_id'])
            self.service_ids = list_fri  
            
        elif self.weekday == 6 and self.date <= '20200301':
            df_sat = pd.DataFrame(df_sat[df_sat['start_date']<20200301])
            list_sat = list(df_sat['service_id'])
            self.service_ids = list_sat
           
        else:
            raise NotImplementedError("Only Friday's and Saturday's before March 2020 Supported!") 
        self.root = Node(self.get_stops())

        
    def get_trips(self, route=None):
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("trips.txt") as f:
                df_trips = pd.read_csv(f)
        list1 = list(self.service_ids)
        list2 = []
        df_trips.set_index('service_id', inplace=True)
        df_trips = df_trips.sort_values(['trip_id'], ascending=True)
        df_trips = df_trips.loc[list1, ['trip_id', 'route_short_name', 'bikes_allowed']]
        d = {1: True, 0: False}
        if route != None:
            df_trips = df_trips[df_trips['route_short_name'] == route]
            trip_id = df_trips['trip_id']
            route_id = df_trips['route_short_name']
            bikes_allowed = df_trips['bikes_allowed'].map(d)
            for i in range(len(df_trips)):
                list2.append(Trip(trip_id[i], route_id[i], bikes_allowed[i]))
        else:
            trip_id = df_trips['trip_id']
            route_id = df_trips['route_short_name']
            bikes_allowed = df_trips['bikes_allowed'].map(d)
            for i in range(len(df_trips)):
                list2.append(Trip(trip_id[i], route_id[i], bikes_allowed[i]))
        return list2
    
    def get_stops(self):
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("trips.txt") as f:
                df_trips = pd.read_csv(f)
                
        list1 = list(self.service_ids)
        df_trips.set_index('service_id', inplace=True)
        df_trips = df_trips.sort_values(['trip_id'], ascending=True)
        df_trips = df_trips.loc[list1, ['trip_id']]
        
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("stop_times.txt") as f:
                df_stop_times = pd.read_csv(f)
                
        list2 = list(df_trips['trip_id'])
        df_stop_times.set_index('trip_id', inplace=True)
        df_stop_times = df_stop_times.loc[list2, ['stop_id']]
        st_list = list(df_stop_times.values)
        
        with ZipFile('mmt_gtfs.zip') as zf:
            with zf.open("stops.txt") as f:
                df_stops = pd.read_csv(f)
                
        df_stops.set_index('stop_id', inplace=True)
        df_stops = df_stops[df_stops.index.isin(st_list)]
        df_stops = df_stops[['stop_lat','stop_lon','wheelchair_boarding']]
        df_stops = df_stops.sort_index(ascending=True)
        df_stop_id = df_stops.index
        df_stop_lat = df_stops['stop_lat'].values
        df_stop_lon = df_stops['stop_lon'].values
        d = {1: True, 0: False}
        wheel_bor = df_stops['wheelchair_boarding'].map(d).values
        stop_list = []
        for i in range(len(df_stops)): 
            loc = Location(latlon = (df_stop_lat[i], df_stop_lon[i]))
            x = Stop(df_stop_id[i], loc, wheel_bor[i])
            stop_list.append(x)    
        return stop_list
   
    def get_stops_rect(self, x, y):        
        stops_in_range = []       
        nodeWithStops = self.get_stops_rect_helper(currRoot=self.root, coord=[x,y], crit=0)      
        for i in range(len(nodeWithStops.stops)):
            if x[0] <= nodeWithStops.stops[i].loc.x <= x[1]:
                if y[0] <= nodeWithStops.stops[i].loc.y <= y[1]:
                    stops_in_range.append(nodeWithStops.stops[i])
        return stops_in_range
                    
    def get_stops_rect_helper(self, currRoot, coord, crit=0): 
        #if currRoot.left != None and currRoot.right != None and currRoot.left != None and currRoot.right != None:              
            if (coord[crit][0] < currRoot.midpoint and coord[crit][1] < currRoot.midpoint):
                if currRoot.left != None and currRoot.right != None:              
                    return self.get_stops_rect_helper(currRoot.left,coord,1-crit)
                else:
                    return currRoot 
            elif (coord[crit][0] >= currRoot.midpoint and coord[crit][1] >= currRoot.midpoint):
                if currRoot.right != None and currRoot.left != None:              
                    return self.get_stops_rect_helper(currRoot.right,coord,1-crit)
                else:
                    return currRoot 
            else:
                return currRoot
            
    def get_stops_circ(self, coord, radius):
        rect = self.get_stops_rect((coord[0]-radius, coord[0]+radius), (coord[1]-radius, coord[1]+radius))
        stops_in_circ = []
        for i in range(len(rect)):
            if ((rect[i].loc.x - coord[0])**2 + (rect[i].loc.y - coord[1])**2) <= radius**2:
                stops_in_circ.append(rect[i])
        return stops_in_circ
         
    def scatter_stops(self,ax):
        lon = []
        lat = []
        wheelchair = []
        df = {}
        stops = self.get_stops()
        for i in range(len(stops)):
            lon.append(stops[i].loc.x)
            lat.append(stops[i].loc.y)
            wheelchair.append(stops[i].wheelchair_boarding)
        df = {'lat':lat, 'lon':lon, 'wheel':wheelchair}
        df_true = pd.DataFrame(df)
        df_true = df_true[df_true['wheel']==True]
        df_false = pd.DataFrame(df)
        df_false = df_false[df_false['wheel']==False]
        df_true.plot.scatter(x='lon',y='lat', ax=ax, color='red',marker='.')
        df_false.plot.scatter(x='lon',y='lat', ax=ax, color='0.7',marker='.')     
    
    def draw_tree(self, ax=None):
        root = self.root
        splits = self.draw_helper(currRoot=root, crit=0, ax=ax)
        return splits
     
    
    def draw_helper(self, currRoot, crit=0, ax=None, lw=10,zorder=0):
        stops = currRoot.stops
        midpoint = currRoot.midpoint
        if crit == 0:
            ax.plot((midpoint, midpoint), (stops[0].loc.y, stops[-1].loc.y), lw=5, color='green', zorder=-10)   # plot x lines
            if currRoot.left != None:
                self.draw_helper(currRoot.left, 1-crit, ax=ax)
            if currRoot.right != None:
                self.draw_helper(currRoot.right, 1-crit, ax=ax)
            else:
                 return currRoot
        elif crit == 1:
            ax.plot((stops[0].loc.x, stops[-1].loc.x), (midpoint, midpoint), lw=5, color='green', zorder=-10)  # plot y lines
            if currRoot.left != None:
                self.draw_helper(currRoot.left, 1-crit, ax=ax)
            if currRoot.right != None:
                self.draw_helper(currRoot.right, 1-crit, ax=ax)
            else:
                 return currRoot
        
    
    def __repr__(self): 
        return "BusDay(Datetime({},{},{}))".format(self.date[:4],self.date[4:6],self.date[6:])

          
class Stop(Location):    
    def __init__(self, stop_id, loc, wheelchair_boarding):
        self.stop_id = stop_id
        self.loc = loc
        self.wheelchair_boarding = wheelchair_boarding
        
    def __repr__(self):
        return 'Stop({}, {}, {})'.format(self.stop_id, self.loc, self.wheelchair_boarding)    

class Node():    
    def __init__(self, stops, level=0):
        self.stops = stops
        self.left = None
        self.right = None
        self.midpoint = 0
        if level < 6:
            if (level%2) == 0:
                stops_x = sorted(stops, key=lambda x: x.loc.x, reverse=False) # checks midpoint, only care about x
                length_x = len(stops_x)               
                self.midpoint = stops_x[length_x//2].loc.x
                self.left = Node(stops_x[:length_x//2],level+1)
                self.right = Node(stops_x[(length_x//2)+1:],level+1)
                #self.stops = stops_x                              
            elif (level % 2) == 1:
                stops_y = sorted(stops, key=lambda x: x.loc.y, reverse=False) # checks midpoint, only care about y
                length_y = len(stops_y)
                self.midpoint = stops_y[length_y//2].loc.y
                self.left = Node(stops_y[:length_y//2],level+1)
                self.right = Node(stops_y[(length_y//2)+1:],level+1)
        else:
            return
            

        
  
     
