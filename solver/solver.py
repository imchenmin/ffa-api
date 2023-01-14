# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 17:14:24 2022

@author: DELL
"""



from solver.route_planning import data_regulation
import copy

from solver.vlt import vlt_select
from solver.vlt import vlt_update

def solver(destination, response, number = 3, threshold = 100):
    """
     #e.g. destination = [114.000591,22.598331]  是求救人的location，分别是求救人的经度，维度,
    #number = 3 派遣志愿者人数，可以是大于等于1的整数，以number = 3 为例，
    #若算法返回的path数量少于3条（至少一条），比如只返回了两条，说明算法认为没有必要再增加一个人
    #threshold 算法暂停参数，可改
    #e.g. response = response = [
     #      {
      #      "id": 1,
       #     "lon": 114.002946,
        #    "lat": 22.601137   #松禾体育场
    #        },
    #       {
    #        "id": 80,
    #        "lon": 114.002451,
    #        "lat": 22.599728   #教师公寓4号楼
    #        },
    #       {
    #        "id": 42,
    #        "lon": 113.995814,
    #        "lat": 22.594767   #台州楼
    #        },
    #       {
    #       "id": 25,
    #       "lon": 113.998378,
    #       "lat": 22.595084   #琳恩图书馆
    #        },
    #       {
    #        "id": 37,
    #        "lon": 114.00076,
    #        "lat": 22.595252  #商学院
    #        },
    #       {
    #        "id": 72,
    #        "lon": 113.995653,
    #        "lat": 22.59961   #工学院大楼
    #        }
    #       ]
    :param destination:
    :param response:
    :param number:
    :param threshold:
    :return:
    """
    policy_dict = {}
    for vlt in response:
        policy_dict[vlt['id']] = data_regulation([vlt['lon'],vlt['lat']], [114.00076,22.59961])

    policy_dist = {}
    for ID,data in policy_dict.items():
        policy_dist[ID] = []
        for path in data[0]:
            policy_dist[ID].append(float(path[0]))
    policy_dist_copy = copy.deepcopy(policy_dist)
    selected_id = []
    path_index = []  

    for i in range(number):
        selection = vlt_select(policy_dist_copy)
        if selection[0] < 0:
            break
        selected_id.append(selection[0])
        path_index.append(selection[1])
        policy_dist_copy = vlt_update(selected_id[-1], path_index[-1], threshold, policy_dist_copy, policy_dict)
    
    response_policy = {}
    for i in range(len(selected_id)):
        response_policy[selected_id[i]] = policy_dict[selected_id[i]][1]['route']['paths'][path_index[i]]

    return response_policy

"""
#policy_dict_4与policy_dict_3返回结果相同，说明在这个例子中，算法认为从三个人
#增加到4个人是不必要的，因此只派遣了三个志愿者并且只返回了三条路径
#number = 3的运行结果（即policy_dict_3）：
#{37: {'distance': '339',
#  'cost': {'duration': '271'},
#  'steps': [{'instruction': '向东北步行96米左转',
#   'orientation': '东北',
#    'road_name': '',
#    'step_distance': '96',
#    'cost': {'duration': '77'},
#    'polyline': '114.001029,22.595043;114.00138,22.59543;114.001432,22.595482;114.001675,22.595668'},
#   {'instruction': '向北步行243米到达目的地',
#    'orientation': '北',
#    'road_name': '',
#    'step_distance': '243',
#    'cost': {'duration': '194'},
#    'polyline': '114.001675,22.595668;114.001246,22.596046;114.000911,22.596376;114.000842,22.596493;114.000842,22.596658;114.000881,22.596888;114.000881,22.596888;114.00105,22.597526'}]},
# 80: {'distance': '398',
#  'cost': {'duration': '318'},
#  'steps': [{'instruction': '向北步行46米左转',
#    'orientation': '北',
#    'road_name': '',
#    'step_distance': '46',
#    'cost': {'duration': '37'},
#    'polyline': '114.002361,22.599796;114.002361,22.599965;114.002361,22.599965;114.002361,22.599987;114.002361,22.599987;114.002352,22.600226'},
#   {'instruction': '沿立心路向西步行177米向左前方行走',
#    'orientation': '西',
#    'road_name': '立心路',
#    'step_distance': '177',
#    'cost': {'duration': '142'},
#    'polyline': '114.002348,22.600226;114.00194,22.600091;114.00194,22.600091;114.001901,22.600082;114.00181,22.600065;114.00181,22.600065;114.001046,22.600043;114.001046,22.600043;114.000885,22.600043;114.000651,22.600056'},
#   {'instruction': '向西南步行69米左转',
#    'orientation': '西南',
#    'road_name': '',
#    'step_distance': '69',
#    'cost': {'duration': '55'},
#    'polyline': '114.000647,22.600056;114.000543,22.599974;114.000317,22.599831;114.000109,22.599692'},
#   {'instruction': '向南步行106米到达目的地',
#    'orientation': '南',
#    'road_name': '',
#    'step_distance': '106',
#    'cost': {'duration': '85'},
#    'polyline': '114.000104,22.599688;114.000326,22.599544;114.000356,22.599479;114.000365,22.599384;114.000139,22.598984;114.000065,22.598928'}]},
# 1: {'distance': '542',
#  'cost': {'duration': '434'},
#  'steps': [{'instruction': '向南步行79米右转',
#    'orientation': '南',
#    'road_name': '',
#    'step_distance': '79',
#    'cost': {'duration': '63'},
#    'polyline': '114.002661,22.601102;114.002691,22.600881;114.00273,22.600742;114.002773,22.600651;114.002895,22.600438'},
#   {'instruction': '向西步行117米左转',
#    'orientation': '西',
#    'road_name': '',
#    'step_distance': '117',
#    'cost': {'duration': '94'},
#    'polyline': '114.002895,22.600434;114.002743,22.600352;114.002587,22.600304;114.002587,22.600304;114.002352,22.60023;114.002352,22.60023;114.00194,22.600091;114.00194,22.600091;114.001901,22.600082;114.00181,22.600065'},
#   {'instruction': '向南步行244米右转',
#   'orientation': '南',
#   'road_name': '',
#    'step_distance': '244',
#    'cost': {'duration': '195'},
#    'polyline': '114.001806,22.600061;114.001858,22.599922;114.001936,22.599822;114.002079,22.599566;114.002096,22.599518;114.002096,22.599475;114.002118,22.59928;114.002118,22.59928;114.002127,22.599115;114.002148,22.599028;114.00217,22.59895;114.002227,22.598815;114.002227,22.598815;114.00224,22.598772;114.002331,22.598589;114.002431,22.598433;114.002431,22.598433;114.002561,22.598203;114.002639,22.598016'},
#   {'instruction': '向西步行48米向左前方行走',
#    'orientation': '西',
#    'road_name': '',
#    'step_distance': '48',
#    'cost': {'duration': '38'},
#    'polyline': '114.002639,22.598012;114.002365,22.598056;114.002365,22.598056;114.002174,22.598103'},
#   {'instruction': '向西步行54米到达目的地',
#    'orientation': '西',
#    'road_name': '',
#    'step_distance': '54',
#    'cost': {'duration': '43'},
#    'polyline': '114.00217,22.598103;114.00204,22.598112;114.001879,22.598038;114.001697,22.597951'}]}}
"""