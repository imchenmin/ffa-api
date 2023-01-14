# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import json

from urllib import request
from solver.dist_overlap import dist_overlap
import requests

from geopy.distance import geodesic
import copy

def data_regulation(origin,destination):
    print(origin, destination)
    O = str(origin[0]) + "," + str(origin[1])
    D = str(destination[0]) + "," + str(destination[1])
    url = 'https://restapi.amap.com/v5/direction/walking?key=f9591c4e8a762e83e72548320123638e&isindoor=0&alternative_route=2&origin={0}&destination={1}&show_fields=cost,polyline'
    html=requests.get(url.format(O,D)).text
    js=json.loads(html)
    policylist = []
    print(js)
    for path in js['route']['paths']:
        d = path['distance']
        steps = path['steps']
        polylinelist = []
        for p in steps:
            polylines = p['polyline'].split(';')
            for polyline in polylines:
                polylinelist.append([float(polyline.split(",")[0]), float(polyline.split(",")[1])])
        policylist.append([d,polylinelist])
    return [policylist, js]
            
  
      
        
   # d = js['route']['paths'][0]['distance']
   # steps=js['route']['paths'][0]['steps']
   # polylinelist = []
   # for p in steps:
   #     polylines = p['polyline'].split(';')
   #     for polyline in polylines:
   #         polylinelist.append([float(polyline.split(",")[0]), float(polyline.split(",")[1])])
   # return [d, polylinelist]
#input: origin = [longtitude,latitude] destination = [longtitude, latitude]
#output = [[path1_distance, polylinelist1], [path2_distance, polylinelist2],...] 1-3 routes

def regularized_distance(x1,x2):
    d = geodesic((x1[1],x1[0]), (x2[1],x2[0])).m
    return d
#input: x1 = [longtitude, latitude], x2 = [longtitude, latitude]
#output: straight line distance between x1 and x2

#origin = [114.000949,22.591727]
#destination = [114.010261,22.599364]

#o1 = [113.99384,22.592174] 
#d1 = [114.002171,22.594235] #惟理门到二号门

#o2 = [113.992064,22.592229]
#d2 = [114.007562,22.596884] #笃学路与学苑大道交叉到四号门

#r1 = data_regulation(o1,d1)
#r1_copy = data_regulation(o1,d1)
#r2 = data_regulation(o2,d2)

#o3 = [113.99288,22.592026] 
#d3 = [114.002595,22.594215] #塘岭路与学苑大道交叉到二号门对面（智园北门）
#r3 = data_regulation(o3,d3)


#输入经纬度坐标x1，x2，返回直线距离。




















    
