#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Configuration
import os
import sys

#__file__ = os.getcwd()

rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from naviutil import NaviPath, NaviFunc, NaviIO
navipath = NaviPath()
navifunc = NaviFunc()
naviio = NaviIO()

import shutil
import itertools
from time import time
import pandas as pd
import pickle as pk
from copy import deepcopy
from collections import defaultdict, Counter


## Data Import
def import_schedule(case_num):
    global activity_book

    try:
        fname_initial_schedule = 'C-{}.xlsx'.format(case_num)
        schedule = naviio.xlsx2schedule(activity_book=activity_book, fname=fname_initial_schedule)
        return schedule
    except FileNotFoundError:
        print('Error: You should run "init.py" first to build "C-{}.xlsx"'.format(case_num))
        sys.exit(1)

## Duplicated Activity Normalization
def normallize_duplicated_activity(schedule):
    global case_num

    schedule_normalized = defaultdict(dict)
    for location in schedule:
        schedule_normalized[location] = {}

        day = 0
        for activity_code in schedule[location].values():
            if activity_code not in schedule_normalized[location].values():
                schedule_normalized[location][day] = activity_code
                day += 1
            else:
                continue
    return schedule_normalized

def find_influence_locations(location_list, current_location, activity_code):
    influenced_locations = []

    try:
        pre_dist = activity_book[activity_code].pre_dist
        if pre_dist == 'NA':
            return []
        else:
            for comparing_location in schedule:
                if comparing_location == current_location:
                    continue
                else:
                    distance = navifunc.euclidean_distance(current_location.split('_'), comparing_location.split('_'))
                    if distance <= pre_dist:
                        influenced_locations.append(comparing_location)
    except KeyError:
        # print('Please add {} to activity_table.xlsx and run init.py again!!'.format(activity_code))
        pass

    return influenced_locations

def check_pre_dist(schedule, location, day, activity_code):
    location_list = list(schedule.keys())
    influenced_locations = find_influence_locations(location_list=location_list, current_location=location, activity_code=activity_code)

    if influenced_locations:
        pass
    else:
        return False

    existing_activity_codes = []
    for influenced_location in influenced_locations:
        try:
            existing_activity_code = schedule[influenced_location][day]
            if existing_activity_code == '------':
                continue
            else:
                existing_activity_codes.append(existing_activity_code)
        except KeyError:
            continue

    if existing_activity_codes:
        return True
    else:
        return False
    
def push_workdays_single_location(schedule, target_location, after):
    schedule_updated = defaultdict(dict)
    for location in schedule:
        if location != target_location:
            schedule_updated[location] = schedule[location]
        else:
            for day, activity_code in schedule[location].items():
                if day >= after:
                    schedule_updated[location][day+1] = activity_code
                else:
                    schedule_updated[location][day] = activity_code
            schedule_updated[location][after] = '------'
    return schedule_updated

def activity_predecessor_completion_constraint(schedule):
    schedule_updated = defaultdict(dict)
    for current_location in schedule:
        for day, activity_code in schedule[current_location].items():
            if check_pre_dist(schedule=schedule, location=current_location, day=day, activity_code=activity_code):
                schedule_updated = deepcopy(push_workdays_single_location(schedule=schedule, target_location=current_location, after=day))
                return schedule_updated
            else:
                continue

    return schedule


if __name__ == '__main__':
    ## Load project
    activity_book = naviio.import_activity_book()

    case_num = '003'
    schedule = import_schedule(case_num)
    schedule_original = normallize_duplicated_activity(schedule)
    navifunc.print_schedule(schedule=schedule_original)

    times = []
    iteration = 0
    while True:
        print('\r  | Iteration: {:,d}'.format(iteration), end='')
        start_time = time()

        schedule_updated = deepcopy(activity_predecessor_completion_constraint(schedule_original))

        if navifunc.compare_schedule(schedule_original, schedule_updated) == 'same':
            break
        else:
            schedule_original = deepcopy(schedule_updated)
            iteration += 1

    end_time = time()
    running_time = end_time - start_time
    times.append((iteration, running_time))
    print(' ({:.03f} sec)'.format(running_time), end='')
    print('\n  | Running time: {} sec'.format(sum([t for _, t in times])))

    navifunc.print_schedule(schedule=schedule_updated)