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
    case_num = '03_excavation_only_updated'
    project = load_project(case_num=case_num)




    fname = 'schedule_N-03_excavation_only_C-updated_I-005.xlsx'
    fdir = '/data/blank54/workspace/project/navi/schedule/'
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