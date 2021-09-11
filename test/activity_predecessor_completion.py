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

from naviutil import NaviPath
navipath = NaviPath()

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


#9월 11일 주피터로 작업한거 옮겨봅니다. 영향을 받는 그리드 영역 찾기까지 했어요!!!
#predecessor_dist
import pandas as pd
from naviutil import NaviPath
navipath = NaviPath()

activity_pre_dist = pd.read_excel(navipath.activity_pre_dist)

activity_pre_dist.head()


#loading activity dist template and making dic

activity_pre_dist_dic = {}
for _, line in activity_pre_dist.iterrows():
    #    print(line)

    #    print(line['code'])
    #    print(line['predecessor_dist'])
    activity_pre_dist_dic[line['code']] = line['predecessor_dist']

activity_pre_dist_dic
print(activity_pre_dist_dic)


#Loading updated schedule
productivity_updated_schedule = pd.read_excel('D:/cns/navi-master/navi/schedule/schedule_N-05_structure_C-updated_I-062.xlsx')
productivity_updated_schedule

#checking activity & dist
productivity_updated_schedule.iloc[3][0]#첫날의 작업 중 첫번째다 치고

check_pre_dist_act = productivity_updated_schedule.iloc[3][0]
checked_dist = activity_pre_dist_dic[check_pre_dist_act] #첫날 첫번째 작업의 선행완료거리값
print(checked_dist)

#grid & activity


# productivity_updated_schedule.columns[0]
#grid_a = productivity_updated_schedule.iloc[3,0] #작업이 있는 첫 그리드를 찾아다 치고
#print(grid_a)


#작업을 가진 그리드 딕셔너리 생성 필요할지는 모르겠음.(현재는 동일 작업으로 함)
act_grids ={}
for grid, activity in productivity_updated_schedule.iterrows():
#     print(activity["Unnamed: 0"]) # grid
#     print(activity[0]) #index
#     print(grid) #index
    grid_list_w_act = {}
    if activity[0] == check_pre_dist_act: #확인된 작업과 동일한 그리드
#         print(activity["Unnamed: 0"])     #확인된 작업과 동일한 그리드 출력
        act_grids[activity["Unnamed: 0"]] = activity[0] #확인된 작업과 동일한 그리드 딕셔너리 생성

print(act_grids)

#finding grids inside influence of act
# checked_dist값 사용
# print(checked_dist)
# x 영향범위
for grid, activity in act_grids.items():
    x, y, z = grid.split("_")
    pre_dist1 = checked_dist
    pre_dist2 = checked_dist
    x = int(x)
    pre_dist_location_x_list = []
    while pre_dist1 > 0:
        pred_dist_x1 = x + pre_dist1
        #         print(pred_dist_x)
        pre_dist_location_x_list.append(pred_dist_x1)
        pre_dist1 = pre_dist1 - 1

    while pre_dist2 >= 0:
        pred_dist_x2 = x - pre_dist2
        #         print(pred_dist_x)
        if pred_dist_x2 > 0:
            pre_dist_location_x_list.append(pred_dist_x2)
        pre_dist2 = pre_dist2 - 1

    print(pre_dist_location_x_list)

# checked_dist값 사용
# print(checked_dist)
# y 영향범위
for grid, activity in act_grids.items():
    x, y, z = grid.split("_")
    pre_dist1 = checked_dist
    pre_dist2 = checked_dist
    y = int(y)
    pre_dist_location_y_list = []
    while pre_dist1 > 0:
        pred_dist_y1 = y + pre_dist1
        #         print(pred_dist_y)
        pre_dist_location_y_list.append(pred_dist_y1)
        pre_dist1 = pre_dist1 - 1

    while pre_dist2 >= 0:
        pred_dist_y2 = y - pre_dist2
        #         print(pred_dist_y)
        if pred_dist_y2 > 0:
            pre_dist_location_y_list.append(pred_dist_y2)
        pre_dist2 = pre_dist2 - 1

    print(pre_dist_location_y_list)

# print(checked_dist)
act_checked = productivity_updated_schedule.iloc[3][0]
# print(act_checked)

# Activity code 맨 앞문자
# print(checked_dist)
# z 영향범위

for grid, activity in act_grids.items():
    x, y, z = grid.split("_")
    pre_dist1 = 1
    pre_dist2 = int(-1)
    z = int(z)
    pre_dist_location_z_list = [z]
    if 'D' in act_checked:
        pred_dist_z = z + pre_dist1
        pre_dist_location_z_list.append(pred_dist_z)
    elif 'S' in act_checked:
        pred_dist_z = z + pre_dist2
        pre_dist_location_z_list.append(pred_dist_z)

    print(pre_dist_location_z_list)

#making influence grid
influence_grids=[]
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
            influence_grid = '_'.join(influence_x_y_z)
            influence_grids.append(influence_grid)

print(influence_grids)

# 자신의 그리드 제거
for grid_except, activity in act_grids.items():
    while grid_except in influence_grids:
        influence_grids.remove(grid_except)

print(influence_grids)



#9월 11일
#영향을 받는 그리드와 첫날 작업 디셔너리 만들기
#해당 그리드 작업과 작업 디셔너리내 작업의 선후관계 비교하여 일정 미루기








def push_workdays_uniformly(schedule, location, after, add):
    schedule_to_modi = deepcopy(schedule)
    for activity_code in schedule_to_modi[location]:
        workday = schedule_to_modi[location][activity_code]
        if workday >= after:
            schedule_to_modi[location][activity_code] += add
    return schedule_to_modi

def compare_schedule(schedule_1, schedule_2):
    if schedule_1.keys() != schedule_2.keys():
        return 'different'
    else:
        pass

    for location in schedule_1.keys():
        if len(schedule_1[location]) != len(schedule_2[location]):
            return 'different'
        else:
            pass

        for activity_code, day in schedule_1[location].items():
            if day != schedule_2[location][activity_code]:
                return 'different'
            else:
                continue

    return 'same'


if __name__ == '__main__':
    ## Load project
    case_num = '03_excavation_only'
    project = load_project(case_num=case_num)



    fname = 'schedule_N-03_excavation_only_C-updated_I-005.xlsx'
    fdir = '/cns/navi-master/navi/schedule'
    fpath = os.path.join(fdir, fname)
    schedule_data = pd.read_excel(fpath)

    schedule = defaultdict(dict)
    for row in schedule_data.iterrows():
        # print(row)
        location = row[1]['Unnamed: 0']
        schedule[location] = {}

        for day, activity_code in row[1].items():
            if day == 'Unnamed: 0':
                continue

            if len(str(activity_code)) == 6:
                schedule[location][activity_code] = day


    iteration = 0
    while True:


        for location in schedule.keys():
            my_start, my_end = find_workdays(activity_list=schedule[location], major_code='D')
            # print(location)
            # print(my_start)
            # print(my_end)
            print('-----------------------------------')

            upper_location = find_upper_location(location)
            if upper_location not in schedule.keys():
                continue
            # print(location)
            # print(upper_location)

            upper_start, upper_end = find_workdays(activity_list=schedule[upper_location], major_code='D')

            try:
                if my_start < upper_end:
                    print(location)
                    print(my_start)
                    print(upper_location)
                    print(upper_end)

                    add = upper_end - my_start + 1
                    print(add)
                    updated_schedule = deepcopy(push_workdays_uniformly(schedule, location, after=my_start, add=add))
                    iteration += 1

                else:
                    continue
            except TypeError:
                continue

        if compare_schedule(schedule, updated_schedule) == 'same':
            break
        else:
            schedule = deepcopy(updated_schedule)
            iteration += 1

    print(iteration)

    schedule_dict = defaultdict(dict)
    for location in updated_schedule:
        for activity_code, day in updated_schedule[location].items():
            schedule_dict[day][location] = activity_code

    schedule_df = pd.DataFrame(schedule_dict)
    schedule_df.to_excel('temp.xlsx', na_rep='', header=True, index=True)