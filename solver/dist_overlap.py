#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 12:44:42 2022

@author: jingjun
"""
import pandas as pd
from geopy import distance
from geopy.distance import geodesic




def yf_regularized_distance(one_row):
    d = geodesic((one_row['y'],one_row['x']), (one_row['dest_y'],one_row['dest_x'])).m
    return d

def cal_dist(one_row):
    return distance.great_circle((one_row['y'],one_row['x']), (one_row['dest_y'],one_row['dest_x'])).m



def dist_overlap(data1, data2):
    data1 = pd.DataFrame(data1)
    data1.columns = ['x','y']
    data2 = pd.DataFrame(data2)
    data2.columns = ['x','y']
    data1['dest_x'] = data1['x'].shift(-1)
    data1['dest_y'] = data1['y'].shift(-1)
    data1.iloc[-1,[-1,-2]] = data1.iloc[-1,[1,0]]
    data1['dist'] = data1.apply(lambda x: yf_regularized_distance(x), axis = 1)
    
    data2['dest_x'] = data2['x'].shift(-1)
    data2['dest_y'] = data2['y'].shift(-1)
    data2.iloc[-1,[-1,-2]] = data2.iloc[-1,[1,0]]
    data2['dist'] = data2.apply(lambda x: yf_regularized_distance(x), axis = 1)
    simi_df = pd.merge(data1, data2, how='inner', on=['x', 'y', 'dest_x', 'dest_y','dist'])
    simi = simi_df['dist'].sum()#/(simi_df['d_x'].min()+simi_df['d_y'].min())
   # print(simi_df)
    return simi
#input data1 = polylinelist1, data2 = polylinelist2
#output = distance of overlap