## Print schedule#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import sys

rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from copy import deepcopy
import pickle as pk
import pandas as pd
from collections import defaultdict

from naviutil import NaviPath, NaviIO, NaviFunc
navipath = NaviPath()
naviio = NaviIO()
navifunc = NaviFunc()

def load_project(case_num):
    with open(navipath.proj(case_num), 'rb') as f:
        project = pk.load(f)

    return project

def calculate_activity_work_plan(schedule):
    work_plan = defaultdict(list)
    for location in schedule:
        for activity_code, day in schedule[location].items():
            work_plan[day].append(activity_code)

    return work_plan

def find_workdays(activity_list, major_code):
    workdays = []
    for activity, day in activity_list.items():
        if major_code in activity:
            workdays.append(day)

    try:
        day_start = min(workdays)
        day_end = max(workdays)
    except ValueError:
        day_start = None
        day_end = None

    return day_start, day_end

def find_upper_location(location):
    x, y, z = location.split('_')
    upper_z = str(int(z) + 1)

    upper_location = '_'.join((x, y, upper_z))
    return upper_location

def find_lower_location(location):
    x, y, z = location.split('_')
    lower_z = str(int(z) - 1 )

    lower_location = '_'.join((x, y, lower_z))
    return lower_location



###############################################################################
#10월15일 수정
#Schedule 딕셔너리를 이제 이해했네요.

import pandas as pd
from naviutil import NaviPath
navipath = NaviPath()

activity_pre_dist = pd.read_excel(navipath.activity_pre_dist)

###############################################################################
#loading activity dist template and making dic
activity_pre_dist_dic = {}
for _, line in activity_pre_dist.iterrows():
    activity_pre_dist_dic[line['code']] = line['predecessor_dist']


###############################################################################
#Loading updated schedule
activity_book = naviio.import_activity_book()
fpath = 'D:/cns/navi-master/navi/schedule/C-003.xlsx'
schedule = naviio.xlsx2schedule(activity_book=activity_book, fpath=fpath)
schedule

###############################################################################
#임의의 첫 위치, 첫 날 작업으로 지정하여 영향거리 그리드 찾기
#checking activity & dist
temp_location = '1_1_0'
day = 0

check_pre_dist_act = schedule[temp_location][day]
checked_dist = activity_pre_dist_dic[check_pre_dist_act] #첫날 첫번째 작업의 선행완료거리값

#finding grids inside influence of act
location_to_check = []
location_to_check.append(temp_location)

for location in location_to_check:
    x, y, z = location.split("_")
    pre_dist1 = checked_dist
    pre_dist2 = checked_dist
    pre_dist_z1 = 1
    pre_dist_z2 = int(-1)
    x = int(x)
    y = int(y)
    z = int(z)
    pre_dist_location_x_list = []
    pre_dist_location_y_list = []
    pre_dist_location_z_list = [z]
    while pre_dist1 > 0:
        pred_dist_x1 = x + pre_dist1
        pre_dist_location_x_list.append(pred_dist_x1)
        pred_dist_y1 = y + pre_dist1
        pre_dist_location_y_list.append(pred_dist_y1)
        pre_dist1 = pre_dist1 - 1

    while pre_dist2 >= 0:
        pred_dist_x2 = x - pre_dist2
        pred_dist_y2 = y - pre_dist2
        if pred_dist_x2 > 0:
            pre_dist_location_x_list.append(pred_dist_x2)
        if pred_dist_y2 > 0:
            pre_dist_location_y_list.append(pred_dist_y2)
        pre_dist2 = pre_dist2 - 1

    # if 'D' in check_pre_dist_act:
    #     pred_dist_z = z + pre_dist_z1
    #     pre_dist_location_z_list.append(pred_dist_z)
    # elif 'S' in check_pre_dist_act:
    #     pred_dist_z = z + pre_dist_z2
    #     pre_dist_location_z_list.append(pred_dist_z)

#making influence grid
#특정 작업의 영향거리 내 Location만들기1

influence_locations=[]
for x in pre_dist_location_x_list:
    x=str(x)
    for y in pre_dist_location_y_list:
        y=str(y)
        for z in pre_dist_location_z_list:
            z=str(z)
            influence_x_y_z = []
            influence_x_y_z.append(x)
            influence_x_y_z.append(y)
            influence_x_y_z.append(z)
            influence_location = '_'.join(influence_x_y_z)
            influence_locations.append(influence_location)

# 자신의 그리드 제거
if temp_location in influence_locations:
    influence_locations.remove(temp_location)

# 존재하는 그리드만 남기기
existing_influence_location=[]
for location in schedule.keys():
    if location in influence_locations:
        existing_influence_location.append(location)
    else:
        continue

###############################################################################
#영향내 그리드의 작업 확인
#activity in influence locations
acts_in_existing_Influence_location = []
for location in existing_influence_location:
       acts_in_existing_Influence_location.append(schedule[location][day])


###############################################################################
#영향내 작업과 임의의 작업 선후 확인
# checking activity logic within influence locations
#acts_in_existing_Influence_location 내 작업이 schedule[temp_location][day] 작업보다 선행인가 확인
activity_order = pd.read_excel(navipath.activity_order)

acts_in_existing_Influence_location
