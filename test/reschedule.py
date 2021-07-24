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

    project.export(fpath=navipath.schedule(case_num))
    return project

def check_activity_order_on_single_location(local_schedule):
    results = []

    activity_sorted_by_day = [activity_code for activity_code, _ in sorted(local_schedule.items(), key=lambda x:x[1], reverse=False)]
    for activity_code_1, activity_code_2 in itertools.combinations(activity_sorted_by_day, r=2):
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

def check_productivity_overload(activity_code, count):
    if count > project.activities[activity_code].productivity:
        return 'overloaded'
    else:
        return 'fine'

def push_workdays(schedule, where, after):
    for activity in schedule[where]:
        workday = schedule[where][activity]
        if workday >= after:
            schedule[where][activity] += 1
    return schedule

def export_schedule(schedule, fpath):
    os.makedirs(os.path.dirname(fpath), exist_ok=True)

    schedule_dict = defaultdict(dict)
    for location in schedule:
        for activity_code, day in schedule[location].items():
            schedule_dict[day][location] = activity_code

    schedule_df = pd.DataFrame(schedule_dict)
    schedule_df.to_excel(fpath, na_rep='', header=True, index=True)

def reschedule(project):
    schedule = defaultdict(dict)
    todo_when = defaultdict(list)
    for work in project.schedule:
        todo_when[work.day].append(work)
        schedule[work.grid.location][work.activity.code] = work.day

    for location in schedule:
        if check_activity_order_on_single_location(local_schedule=schedule[location]) == 'conflict':
            ## Reorder activities in the location
            print('TODO')
        else:
            continue

    for day, works in sorted(todo_when.items(), key=lambda x:x[0], reverse=False):
        activity_counter = Counter([work.activity.code for work in works])
        for activity_code, count in activity_counter.items():
            if check_productivity_overload(activity_code, count) == 'overloaded':
                num_overloaded = (count-project.activities[activity_code].productivity)
                for target_work in [work for work in works if work.activity.code == activity_code][:num_overloaded]:
                    schedule = deepcopy(push_workdays(schedule, where=target_work.grid.location, after=target_work.day))
            else:
                continue

    fpath=navipath.reschedule(case_num)
    export_schedule(schedule, fpath)



if __name__ == '__main__':
    ## Load project
    case_num = '03'
    project = load_project(case_num=case_num)
    # project.summary(duration=True, sorted_grids=True)

    ## Reschedule
    reschedule(project)