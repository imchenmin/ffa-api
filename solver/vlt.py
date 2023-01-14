# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 20:43:33 2022

@author: DELL
"""
from solver.dist_overlap import dist_overlap

def vlt_select(policy_dist, bigM = 10000):
    ID1 = -100
    index1 = -100
    min_dist = bigM    
    for ID,policy in policy_dist.items():
        if min(policy) < min_dist:
            ID1 = ID
            min_dist = min(policy)
            index1 = policy.index(min(policy))
    return [ID1, index1]

def vlt_update(ID, index, threshold, policy_dist_copy, policydict,bigM = 10000):
    basepath = policydict[ID][0][index][1]
    for ID1, dist in policy_dist_copy.items():
        for i in range(len(dist)):
            if dist_overlap(basepath, policydict[ID1][0][i][1]) > threshold:
                dist[i] = bigM           
    policy_dist_copy.pop(ID)
    return(policy_dist_copy)


























































































































