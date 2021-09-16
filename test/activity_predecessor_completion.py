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


#9월13일 주피터로 작업본 옮깁니다. pre_dist_clean_ver1
#코멘트주신 거 반영하고 영향 받는 로케이션과 작업 디셔너리 만드는거 코드 하나 축가했습니다.
#고작 5줄인데 고민 많이 했네요 ㅎㅎ

import pandas as pd
from naviutil import NaviPath
navipath = NaviPath()

activity_pre_dist = pd.read_excel(navipath.activity_pre_dist)

#loading activity dist template and making dic
activity_pre_dist_dic = {}
for _, line in activity_pre_dist.iterrows():
    activity_pre_dist_dic[line['code']] = line['predecessor_dist']

print(activity_pre_dist_dic)

#Loading updated schedule
# schedule = pd.read_excel('D:/cns/navi-master/navi/schedule/schedule_N-05_structure_C-updated_I-062.xlsx')
# schedule


'''COMMENT
현재 코드에서는 schedule을 DataFrame 형태로 사용하고 계시네요. 호환성을 위해, schedule을 읽어오실 땐 아래의 코드를 사용해주시면 좋겠습니다.
단, 실행하기 전에 "run/init.py"를 한번 실행해주셔야 "activity_book.pk"가 정상적으로 작동합니다. (최초 한번만 실행해주시면 됩니다.)

이렇게 불러온 schedule은 location->day->activity_code로 iterate하는 dictionary입니다.
아래에서 "productivity_updated_schedule.iloc[3][0]"이라고 쓴 코드는 "schedule[특정 location][특정 day]"로 치환할 수 있겠습니다.
이런 방식으로 Line 122-148를 수정해주세요.
'''



'''NOTE
"naviutil.py"에 NaviIO라는 클래스를 추가했습니다.
앞으로 파일을 읽고쓰는데 사용되는 함수를 모아놓을 예정입니다.

지난 코드에서는 activity_book을 읽어오는데 문제가 있어서 에러가 발생했던 것 같습니다.
2021.09.14. 현재 제 컴퓨터에서는 잘 실행되는 것을 확인했습니다.
여전히 에러가 발생한다면 "run/init.py"를 다시 실행해주세요.
'''



activity_book = naviio.import_activity_book()
fpath = 'D:/cns/navi-master/navi/schedule/schedule_N-05_structure_C-updated_I-062.xlsx'
schedule = naviio.xlsx2schedule(activity_book=activity_book, fpath=fpath)

# 여기는 안되서 일단 옮겨만 놨습니다.

#checking activity & dist
schedule.iloc[3][0]#첫날의 작업 중 첫번째다 치고
check_pre_dist_act = schedule.iloc[3][0]
checked_dist = activity_pre_dist_dic[check_pre_dist_act] #첫날 첫번째 작업의 선행완료거리값
print(checked_dist)

#grid & activity
act_grids ={}
for location, activity in schedule.iterrows():
    if activity[0] == check_pre_dist_act: #확인된 작업과 동일한 그리드
        act_grids[activity["Unnamed: 0"]] = activity[0] #확인된 작업과 동일한 그리드 딕셔너리 생성
print(act_grids)

#finding grids inside influence of act
for grid, activity in act_grids.items():
    x, y, z = grid.split("_")
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

    if 'D' in check_pre_dist_act:
        pred_dist_z = z + pre_dist_z1
        pre_dist_location_z_list.append(pred_dist_z)
    elif 'S' in check_pre_dist_act:
        pred_dist_z = z + pre_dist_z2
        pre_dist_location_z_list.append(pred_dist_z)

    print(pre_dist_location_x_list,pre_dist_location_y_list,pre_dist_location_z_list)

#making influence grid
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
print(influence_locations)

# 자신의 그리드 제거
for location_except, activity in act_grids.items():
    while location_except in influence_locations:
        influence_locations.remove(location_except)
print(influence_locations)

#activity in influence locations
# location 리스트와 그날의 작업리스트 중 influence location에 있는 거만 작업리스트 만들기
acts_in_Influence_locations = {}
for location, activity in schedule.iterrows():
    if activity["Unnamed: 0"] in influence_locations:
        acts_in_Influence_locations[activity["Unnamed: 0"]] = activity[1:20]  # 1은 day로 치환 필요

print(acts_in_Influence_locations)

#아래는 작업 중
#checking activity logic with influence locations

activity_order = pd.read_excel(navipath.activity_order)
activity_order.head()



