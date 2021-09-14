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

# 작성하신 코드를 변형해서 활용해보려고 합니다. 아직 이거로 가능한지는 모르겠네요.

# def set_orders_in_activity_book():
#     global fname_activity_book

#     with open(os.path.sep.join((navipath.fdir_component, fname_activity_book)), 'rb') as f:
#         activity_book = pk.load(f)

#     activity_order = pd.read_excel(navipath.activity_order)
#     key_errors = []
#     for _, line in activity_order.iterrows():
#         predecessor_code = line['predecessor']
#         successor_code = line['successor']

#         try:
#             predecessor_activity = deepcopy(activity_book[predecessor_code])
#         except KeyError:
#             key_errors.append(predecessor_code)
#             continue
#         try:
#             successor_activity = deepcopy(activity_book[successor_code])
#         except KeyError:
#             key_errors.append(successor_code)
#             continue

#         predecessor_activity.add_successor(successor_activity.code)
#         successor_activity.add_predecessor(predecessor_activity.code)

#         activity_book[predecessor_code] = predecessor_activity
#         activity_book[successor_code] = successor_activity

#     updates = [True]
#     while any(updates) == True:
#         updates = []
#         for activity_code in activity_book:
#             activity = activity_book[activity_code]

#             existing_preds = deepcopy(list(set(activity.predecessor)))
#             for pred_code in activity.predecessor:
#                 pred_of_pred = list(set(activity_book[pred_code].predecessor))
#                 updated_preds = deepcopy(list(set(existing_preds+pred_of_pred)))
#                 if set(updated_preds) != set(existing_preds):
#                     activity_book[activity_code].predecessor = updated_preds
#                     updates.append(True)

#             existing_succs = deepcopy(list(set(activity.successor)))
#             for succ_code in activity.successor:
#                 succ_of_succ = list(set(activity_book[succ_code].successor))
#                 updated_succs = deepcopy(list(set(existing_succs+succ_of_succ)))
#                 if set(updated_succs) != set(existing_succs):
#                     activity_book[activity_code].successor = updated_succs
#                     updates.append(True)

#     with open(os.path.sep.join((navipath.fdir_component, fname_activity_book)), 'wb') as f:
#         pk.dump(activity_book, f)

#     print('============================================================')
#     print('Set order information to ActivityBook')
#     print('  | fdir : {}'.format(navipath.fdir_component))
#     print('  | fname: {}'.format(fname_activity_book))

#     if key_errors:
#         print('Errors on ActivityOrder template')
#         key_errors = list(set(key_errors))
#         for activity_code in key_errors:
#             print('  | Absent in ActivityBook: {}'.format(activity_code))
#     else:
#         pass


#제 제약조건상에 오류를 발견했어요....
#골조 Workpackage(우리 파일에 Major Actiity)에 세부 작업 먹놓기.... 타설, 양생까지 작업이 있다면
#하부층의 양생이 완료된 후에 상부층 먹놓기가 가능하니까,,, 그냥 선후 작업만 확인해서는 안되네요
#동일층에서는 먹놓기 생산성 만큼 마무리 되면 다른 구역의 먹놓기 작업이 진행가능....
#제약조건이 추가되어야 하네요....
#머리가 좀 아프므로, 레벨의 변화 없이 동일 레벨에서 작업하는거로 데이타 파일을 다시 구성해야겠습니다.
#1층 골조와 2....층 골조 Code를 다르게해서 선후 조건을 걸어야겠어요.... 고민....

#그리고 대세에 영향이 없을 수 있으므로...
#동일층 내에서 공정계획 자동화하는거에 집중하고
#추가로 생산성 고려할때 가까운 location을 우선배정하는거 까지만 제약 추가하고
#시각화 좀 고민하고
#논문작성에 집중해볼까합니다.
#그래도 희망이 보이네요^^ 감사해요

