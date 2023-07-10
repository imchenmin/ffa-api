# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 17:29:49 2022

@author: DELL
"""
import time
from solver import solver
response = [
       {
        "id": 1,
        "lon": 114.002946,
        "lat": 22.601137   #松禾体育场
        },
       {
        "id": 80,
        "lon": 114.002451,
        "lat": 22.599728   #教师公寓4号楼
        },
       {
        "id": 42,
        "lon": 113.995814,
        "lat": 22.594767   #台州楼     
        },
       {
       "id": 25,
       "lon": 113.998378,
       "lat": 22.595084   #琳恩图书馆
        },
       {
        "id": 37,
        "lon": 114.00076,
        "lat": 22.595252  #商学院
        },
       {
        "id": 72,
        "lon": 113.995653,
        "lat": 22.59961   #工学院大楼
        }      
       ]       
time_start = time.time()
policy_dict_3 = solver([114.000591,22.598331], response, number = 3, threshold = 100)
time_end = time.time()
time_c = time_end - time_start
#print(policy_dict_3)
print('time cost', time_c, 's')

time_start = time.time()
policy_dict_4 = solver([114.000591,22.598331], response, number = 4, threshold = 100)
time_end = time.time()
time_c = time_end - time_start
#print(policy_dict_4)
print('time cost', time_c, 's')

