#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import sys
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from naviutil import NaviPath
navipath = NaviPath()

import itertools
import pandas as pd
import pickle as pk
from copy import deepcopy
from collections import defaultdict, Counter


def load_project(case_num):
    with open(navipath.proj(case_num), 'rb') as f:
        project = pk.load(f)

    project.export(fpath=navipath.schedule(case_num, 'step_0_initial'))
    return project

def sort_local_schedule(local_schedule):
    return sorted(local_schedule.items(), key=lambda x:x[1], reverse=False)


## Duplicated Activity Normalization
def norlamlize_duplicated_activity(local_schedule):
    local_schedule_modi = {}

    day = 0
    for activity_code in local_schedule.keys():
        if activity_code not in local_schedule_modi.keys():
            local_schedule_modi[activity_code] = day
            day += 1
        else:
            continue

    return local_schedule_modi


## Activity Order Constraint
def check_activity_order_on_single_location(local_schedule):
    global project
    results = []

    activity_sorted_by_day = {workday: activity_code for activity_code, workday in sorted(local_schedule.items(), key=lambda x:x[1], reverse=False)}
    for activity_code_1, activity_code_2 in itertools.combinations(activity_sorted_by_day.values(), r=2):
        activity_1 = project.activities[activity_code_1]
        activity_2 = project.activities[activity_code_2]

        if activity_code_2 in activity_1.successor:
            results.append('fine')
        elif activity_code_2 in activity_1.predecessor:
            results.append('conflict')
        else:
            results.append('irrelevant')

    if any([result == 'conflict' for result in results]):
        return 'conflict'
    else:
        return 'fine'

def reorder_activity_uniformly_on_single_range(local_schedule, day_from, day_to):
    for a, d in local_schedule.items():
        if d > day_from and d <= day_to:
            local_schedule[a] -= 1
    return local_schedule

def push_workdays_reordering(local_schedule):
    global project

    local_schedule_modi = None
    for activity_code, workday in local_schedule.items():
        activity = project.activities[activity_code]
        later_activity_list = {a: d for a, d in local_schedule.items() if d > workday}

        target_days = []
        for later_activity_code, later_activity_day in later_activity_list.items():
            if later_activity_code in activity.predecessor:
                target_days.append(later_activity_day)

        if not target_days:
            continue
        else:
            break_point = max(target_days)
            local_schedule_modi = reorder_activity_uniformly_on_single_range(local_schedule, day_from=workday, day_to=break_point)
            local_schedule[activity_code] = break_point

    return local_schedule_modi


## Activity Productivity Constraint
def check_productivity_overload(activity_code, count):
    if count > project.activities[activity_code].productivity:
        return 'overloaded'
    else:
        return 'fine'

def push_workdays_uniformly(where, after):
    global project

    schedule_to_modi = deepcopy(project.schedule)
    for activity_code in schedule_to_modi[where]:
        workday = schedule_to_modi[where][activity_code]
        if workday >= after:
            schedule_to_modi[where][activity_code] += 1
    return schedule_to_modi


## Update schedule
def update_schedule(project):
    todo_when = defaultdict(list)

    for location in project.schedule:
        for activity_code, day in project.schedule[location].items():
            todo_when[day].append(activity_code)

    ## Duplicated Activity Normalization
    for location in project.schedule:
        project.schedule[location] = deepcopy(norlamlize_duplicated_activity(local_schedule=project.schedule[location]))

    ## Activity Order Constraint
    for location in project.schedule:
        if check_activity_order_on_single_location(local_schedule=project.schedule[location]) == 'conflict':
            project.schedule[location] = deepcopy(push_workdays_reordering(local_schedule=project.schedule[location]))
        else:
            continue
    project.export(fpath=navipath.schedule(case_num, 'step_1_order'))

    ## Activity Productivity Constraint
    for day, works in sorted(todo_when.items(), key=lambda x:x[0], reverse=False):
        activity_counter = Counter(works)
        for activity_code, count in activity_counter.items():
            if check_productivity_overload(activity_code, count) == 'overloaded':
                num_overloaded = (count-project.activities[activity_code].productivity)
                
                target_location_list = []
                for location in project.schedule.keys():
                    try:
                        if project.schedule[location][activity_code] == day:
                            target_location_list.append(location)
                    except KeyError:
                        continue

                for target_location in target_location_list[:num_overloaded]:
                    project.schedule = deepcopy(push_workdays_uniformly(where=target_location, after=day))
            else:
                continue
    project.export(fpath=navipath.schedule(case_num, 'step_2_productivity'))
    

if __name__ == '__main__':
    ## Load project
    case_num = '03'
    project = load_project(case_num=case_num)
    # project.summary(duration=True, sorted_grids=True)

    ## Update schedule
    update_schedule(project)