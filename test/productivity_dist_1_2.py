import os
import sys
import itertools
import pickle as pk
import pandas as pd
from copy import deepcopy
from collections import defaultdict
from collections import defaultdict, Counter
from object import  Activity, Grid, Project
from naviutil import NaviPath, NaviFunc, NaviIO
navipath = NaviPath()
navifunc = NaviFunc()
naviio = NaviIO()

activity_productivity = pd.read_excel(navipath.activity_table)
activity_productivity.head()

###############################################################################
#loading activity dist template and making dic
###############################################################################
activity_productivity_dic = {}
for _, line in activity_productivity.iterrows():
    activity_productivity_dic[line['code']] = line['productivity']

###############################################################################
#Loading updated schedule
###############################################################################
activity_book = naviio.import_activity_book()
fpath = 'D:/cns/navi-master/navi/schedule/C-003.xlsx'
schedule = naviio.xlsx2schedule(activity_book=activity_book, fpath=fpath)
schedule

###############################################################################
#임의의 첫 위치, 첫 날 작업으로 지정하여 1의 거리 내 동일작업 그리드 찾기
#checking activity & dist
###############################################################################
temp_location = '1_1_0'
day = 0

check_productivity_act = schedule[temp_location][day]
checked_productivity = activity_productivity_dic[check_productivity_act] #첫날 첫번째 작업의 선행완료거리값

###############################################################################
# finding grids inside dist1 act
###############################################################################
location_to_check = []
location_to_check.append(temp_location)

for location in location_to_check:
    x, y, z = location.split("_")
    dist1 = 1
    dist2 = 1
    dist_z1 = 1
    dist_z2 = int(-1)
    x = int(x)
    y = int(y)
    z = int(z)
    dist1_location_x_list = []
    dist1_location_y_list = []
    dist1_location_z_list = [z]
    dist_x1 = x + dist1
    dist1_location_x_list.append(dist_x1)
    dist_y1 = y + dist1
    dist1_location_y_list.append(dist_y1)
    while dist2 >= 0:
        dist_x2 = x - dist2
        dist_y2 = y - dist2
        if dist_x2 > 0:
            dist1_location_x_list.append(dist_x2)
        if dist_y2 > 0:
            dist1_location_y_list.append(dist_y2)
        dist2 = dist2 - 1

        #     if 'D' in check_pre_dist_act:
        #         pred_dist_z = z + pre_dist_z1
        #         pre_dist_location_z_list.append(pred_dist_z)
        #     elif 'S' in check_pre_dist_act:
        #         pred_dist_z = z + pre_dist_z2
        #         pre_dist_location_z_list.append(pred_dist_z)

# making influence grid
# 특정 작업의 영향거리 내 Location만들기1
dist1_locations = []
for x in dist1_location_x_list:
    x = str(x)
    for y in dist1_location_y_list:
        y = str(y)
        for z in dist1_location_z_list:
            z = str(z)
            dist1_x_y_z = []
            dist1_x_y_z.append(x)
            dist1_x_y_z.append(y)
            dist1_x_y_z.append(z)
            dist1_location = '_'.join(dist1_x_y_z)
            dist1_locations.append(dist1_location)

# 자신의 그리드 제거
if temp_location in dist1_locations:
    dist1_locations.remove(temp_location)

# 존재하는 그리드만 남기기
existing_dist1_location = []
for location in schedule.keys():
    if location in dist1_locations:
        existing_dist1_location.append(location)
    else:
        continue

###############################################################################
# 거리1 그리드의 작업 확인
# activity in dist1_locations
###############################################################################
acts_in_existing_dist1_location = []
for location in existing_dist1_location:
    acts_in_existing_dist1_location.append(schedule[location][day])

###############################################################################
#finding grids inside dist2 act
###############################################################################
location_to_check = []
location_to_check.append(temp_location)

for location in location_to_check:
    x, y, z = location.split("_")
    dist1 = 2
    dist2 = 2
    dist_z1 = 1
    dist_z2 = int(-1)
    x = int(x)
    y = int(y)
    z = int(z)
    dist2_location_x_list = []
    dist2_location_y_list = []
    dist2_location_z_list = [z]
    dist_x1 = x + dist1
    dist2_location_x_list.append(dist_x1)
    dist_y1 = y + dist1
    dist2_location_y_list.append(dist_y1)
    while dist2 >= 0:
        dist_x2 = x - dist2
        dist_y2 = y - dist2
        if dist_x2 > 0:
            dist2_location_x_list.append(dist_x2)
        if dist_y2 > 0:
            dist2_location_y_list.append(dist_y2)
        dist2 = dist2 - 2

#making influence grid
#특정 작업의 영향거리 내 Location만들기1
dist2_locations=[]
for x in dist2_location_x_list:
    x=str(x)
    for y in dist2_location_y_list:
        y=str(y)
        for z in dist2_location_z_list:
            z=str(z)
            dist2_x_y_z = []
            dist2_x_y_z.append(x)
            dist2_x_y_z.append(y)
            dist2_x_y_z.append(z)
            dist2_location = '_'.join(dist2_x_y_z)
            dist2_locations.append(dist2_location)


# 자신의 그리드 제거
if temp_location in dist2_locations:
    dist2_locations.remove(temp_location)

# 존재하는 그리드만 남기기
existing_dist2_location=[]
for location in schedule.keys():
    if location in dist2_locations:
        existing_dist2_location.append(location)
    else:
        continue

###############################################################################
#거리2 그리드의 작업 확인
#activity in dist1_locations
###############################################################################
acts_in_existing_dist2_location = []
for location in existing_dist2_location:
       acts_in_existing_dist2_location.append(schedule[location][day])

print(acts_in_existing_dist2_location)