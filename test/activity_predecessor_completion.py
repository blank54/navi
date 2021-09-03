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


#8월29일 추가
# update schedule파일을 가져온다
# def load_project(case_num):
# 날짜와 그리드별 작업 리스트를 가져온다.

# 첫 그리드(예, 2_2_1)에 배정된 작업과 작업의 선행완료 거리값을 확인한다.
# 예를 들어 거리값이 3을 확인한다.

def act_pred_dist(location, activity):
    return predecessor_dist

#     activity_pre_dist = os.path.sep.join((fdir_template, 'activity_pre_dist.xlsx'))
#     activity_pre_dist = pd.read_excel(navipath.activity_pre_dist)
#
#     for _, line in activity_pre_dist.iterrows():

# 어찌할지...모르겠네요 def set_navisystem(): 참조함.
#         code = line['code']
#         predecessor_dist = line['predecessor_dist']
#         parameters = {
#             'code':code
#             'predecessor_dist':predecessor_dist
#         activities[code] = Activity(parameters=parameters)
#        .....


# 거리값내에 포함된 그리드 리스트를 만든다.

def find_pre_dist_location_x_list(location, predecessor_dist):
    return pre_dist_location_x_list

    # 그리드 x값에 거리값을 더하고 뺀값을 리스트로 추가
    # x+3, x+2, x+1, x+0, x-1, x-2, x-3 (예, 2_2_1 =>  x=2, 5,4,3,2,1,0,-1)
    # x는 0보다 커야한다. 0보다 작으면 무시 (예, 2_2_1 =>  x=2, 5,4,3,2,1))
    # x는 그리드 최대값보다 작아야한다. 최대값보다 크면 제거 (예, 2_2_1 =>  max(x)= 4, x=4,3,2,1))

    x, y, z = location.split('_')
    pred_dist_value = act_pred_dist(location, activity)  # 파일 activity_pre_dist.xlsx의 작업별 거리정의 값(2열)
    pre_dist_location_x_list = []
    while pred_dist_value > 0
        pred_dist_x = int(x + pred_dist_value)
        pre_dist_location_x_list += pred_dist_x

    while pred_dist_value > 0 and x > 0
        pred_dist_x = int(x - pred_dist_value)
        pre_dist_location_x_list += pred_dist_x

    return pre_dist_location_y_list


def find_pre_dist_location_y_list(location, predecessor_dist):
    # 그리드 y값에 거리값을 더하고 뺀값을 리스트로 추가
    # y+3, y+2, y+1, y+0, y-1, y-2, y-3 (예, 2_2_1 =>  y=2, 5,4,3,2,1,0,-1)
    # y는 0보다 커야한다. 0보다 작으면 제거 무시 (예, 2_2_1 =>  y=2, 5,4,3,2,1))
    # y는 그리드 최대값보다 작아야한다. 최대값보다 크면 제거 (예, 2_2_1 =>  max(y)=4, y=4,3,2,1))

    x, y, z = location.split('_')
    pred_dist_value = act_pred_dist(location, activity)  # 파일 activity_pre_dist.xlsx의 작업별 거리정의 값(2열)
    pre_dist_location_y_list = []
    while pred_dist_value > 0:
        pred_dist_y = int(y + pred_dist_value)
        pre_dist_location_y_list += pred_dist_y

    while pred_dist_value > 0 and y > 0:
        pred_dist_y = int(y - pred_dist_value)
        pre_dist_location_y_list += pred_dist_y

    return pre_dist_location_y_list

def find_pre_dist_location_z_list(location, activity_code):
    # 그리드 z값은 동일
    # z+0 (예, 2_2_1 =>  z=1, 1))
    # 단 Activity code가 D 인거는 z+0과 z+1값을 리스트로 가집
    # 단 Activity code가 S 인거는 z+0과 z-1값을 리스트로 가집

    x, y, z = location.split('_')
    pre_dist_location_z_list = [z]
    if activity_code in "D":
        pre_dist_location_z_list += z + 1

    elif activity_code in "S":
        pre_dist_location_z_list += z - 1

    else:
        pre_dist_location_z_list = z

    return pre_dist_location_z_list

def make_pre_dist_location_list(location, pre_dist_location_x_list, pre_dist_location_y_list, pre_dist_location_z_list):

    # 그리드 x 첫번째와 y값 전체, z값 결합
    # 그리드 x 두번째와 y값 전체, z값 결합
    # ...
    # 그리드 x 마지막번째와 y값 전체, z값 결합
    # 거리값내 있는 그리드 리스트를 만든다 (예, 2_2_1 => 5_5_1, 5_4_1, 5_3_1, 5_2_1, 5_1_1, 4_5_1,,... )
    # 자신의 그리드는 제외한다.

    # for i in range(len(pre_dist_location_x_list):
    #     pre_dist_location_x_list[i]
    # for pred_dist_y in pre_dist_location_y_list:
    #     for pred_dist_z in pre_dist_location_z_list:
    # pred_dist_location = '_'.join(pre_dist_location_x_list[i], pre_dist_location_y_list[0], pre_dist_location_z_list[0])
    #
    # pred_dist_location_list += pred_dist_location
    # pred_dist_location_list.pop(location)
    # return pre_dist_location_list

def make_pre_dist_activity_list(updated_schedule, pre_dist_location_list):
    # 그리드 리스트에 배정되어 있는 Activity 리스트를 만든다.
    return pre_dist_activity_list



def check_pre_dist_activity_list(location, pre_dist_activity_list):
    # 그리드 리스트에 배정된 Activity 리스트와 기준 그리드의 작업과 선후비교한다.
    # 특정 그리드(예, 2_2_1)에 배정된 작업과 선행작업 여부 검토
    # 선행작업 있으면 작업을 민다

    if 리스트에 선행작업이 있으면:
        일정을
        민다
    else:
        일정을
        유지한다.



###8월29일


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