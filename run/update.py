#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Configuration
import os
import sys
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

    fname = 'C-{}/normalized.xlsx'.format(case_num)
    fdir = os.path.sep.join((navipath.fdir_schedule, os.path.dirname(fname)))
    if os.path.exists(fdir):
        shutil.rmtree(fdir)
    os.makedirs(fdir)
    naviio.schedule2xlsx(schedule_normalized, fname, verbose=False)
    return schedule_normalized

## Modify Schedule
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

## Activity Order Constraint
def check_activity_order_within_work(local_schedule, activity_code):
    global activity_book

    workday = [day for day in local_schedule.keys() if local_schedule[day] == activity_code][0]

    conflict_items = []
    for day in range(workday, max(local_schedule.keys())+1, 1):
        try:
            activity_code2 = local_schedule[day]
            activity_1 = activity_book[activity_code]
            activity_2 = activity_book[activity_code2]
        except KeyError:
            continue
        
        if activity_code2 in activity_1.successor:
            order = 'fine'
        elif activity_code2 in activity_1.predecessor:
            order = 'conflict'
        else:
            order = 'irrelevant'

        if order == 'conflict':
            conflict_items.append((day, activity_code2))

    return conflict_items

def reorder_activity(local_schedule, activity_code, conflict_items):
    local_schedule_updated = {}

    current = [day for day in local_schedule.keys() if local_schedule[day] == activity_code][0]
    move_to = max([day for day, _ in conflict_items])

    for day in range(0, len(local_schedule), 1):
        if day < current or day > move_to:
            local_schedule_updated[day] = local_schedule[day]
        elif day == current:
            local_schedule_updated[move_to] = local_schedule[day]
        else:
            local_schedule_updated[day-1] = local_schedule[day]

    return {d: a for d, a in sorted(local_schedule_updated.items(), key=lambda x:x[0])}

def update_order_in_local_schedule(local_schedule, verbose_local=False, verbose_conflict=False):
    for day, activity_code in sorted(local_schedule.items(), key=lambda x:x[0]):
        conflict_items = check_activity_order_within_work(local_schedule, activity_code)
        
        if verbose_local:
            print('{:2}: {}'.format(day, activity_code))
        else:
            pass

        if conflict_items:
            if verbose_conflict:
                for conflicted_day, conflicted_activity_code in conflict_items:
                    print('  | Conflicts at {}({}) <-> {}({})'.format(activity_code, day, conflicted_activity_code, conflicted_day))
            else:
                pass

            local_schedule_updated = deepcopy(reorder_activity(local_schedule, activity_code, conflict_items))
            return local_schedule_updated
        else:
            continue

    return local_schedule

def activity_order_constraint(schedule, verbose_iter=False, verbose_local=False, verbose_conflict=False):
    schedule_updated = deepcopy(schedule)

    iteration = 0
    for location in schedule.keys():
        local_schedule_original = deepcopy(schedule[location])

        while True:
            iteration += 1

            if verbose_iter:
                print('============================================================')
                print('Iteration: {:03,d} ({})'.format(iteration, location))
            else:
                pass

            local_schedule_updated = deepcopy(update_order_in_local_schedule(local_schedule=local_schedule_original, verbose_local=verbose_local, verbose_conflict=verbose_conflict))
            if navifunc.compare_local_schedule(local_schedule_original, local_schedule_updated) == 'same':
                schedule_updated[location] = deepcopy(local_schedule_updated)
                break
            else:
                local_schedule_original = deepcopy(local_schedule_updated)

    return schedule_updated


# 작업별 순서에 정수값을 줄 수는 없을까요, 10000, 5자리 숫자 중 100의자리 이상은 선후관계 따라 부여
# 10의 자리 수는 선후관계가 없는 것들끼리 이름순 등 랜덤

## Activity Predecessor Distance Constraint
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

## Activity Productivity Constraint
def check_productivity_overload(activity_code, count):
    try:
        if count > activity_book[activity_code].productivity:
            return 'overloaded'
        else:
            return 'fine'
    except KeyError:
        return 'fine'

def activity_productivity_constraint(schedule):
    global activity_book

    daily_work_plan = navifunc.build_daily_work_plan(schedule)
    schedule_updated = defaultdict(dict)
    for day, works in sorted(daily_work_plan.items(), key=lambda x:x[0], reverse=False):
        activity_counter = Counter(works)
        for activity_code, count in activity_counter.items():
            if check_productivity_overload(activity_code, count) == 'overloaded':
                num_overloaded = (count-activity_book[activity_code].productivity)

                target_location_list = []
                for location in schedule.keys():
                    try:
                        if schedule[location][day] == activity_code:
                            target_location_list.append(location)
                    except KeyError:
                        continue

                for target_location in target_location_list[:num_overloaded]:
                    schedule_updated = deepcopy(push_workdays_single_location(schedule=schedule, target_location=target_location, after=day))
            else:
                continue

    if schedule_updated:
        return schedule_updated
    else:
        return schedule


## Compress schedule
def compress_schedule(schedule):
    daily_work_plan = navifunc.build_daily_work_plan(schedule)
    schedule_updated = defaultdict(dict)

    target_day = []
    for day, works in sorted(daily_work_plan.items(), key=lambda x:x[0], reverse=False):
        activity_list = []
        for location, activity_code in works.items():
            if activity_code == '------':
                continue
            else:
                activity_list.append(activity_code)

        if activity_list:
            continue
        else:
            target_day = list(set(target_day))

    if not target_day:
        return schedule
    else:
        compressed_days = 0
        for location in schedule:
            for day, activity_code in schedule[location].items():
                if day in target_day:
                    compressed_days += 1
                    continue
                else:
                    schedule_updated[location][day-compressed_days] = activity_code
        
        return schedule_updated


## Update schedule
def update(schedule_original, save_log):
    times = []
    iteration = 0
    running_time = 0

    while True:
        print('\r  | Iteration: {:,d}'.format(iteration), end='')
        start_time = time()
        
        ## Activity Order Constraint
        schedule_updated_order = deepcopy(activity_order_constraint(schedule_original, verbose_iter=False, verbose_local=False, verbose_conflict=False))

        ## Activity Predecessor Completion Constraint
        schedule_updated_pre_dist = deepcopy(activity_predecessor_completion_constraint(schedule_updated_order))

        ## Activity Productivity Constraint
        schedule_updated_productivity = deepcopy(activity_productivity_constraint(schedule_updated_pre_dist))

        ## Compress empty workday
        schedule_updated_compressed = deepcopy(compress_schedule(schedule_updated_productivity))

        schedule_updated = deepcopy(schedule_updated_compressed)
        if navifunc.compare_schedule(schedule_original, schedule_updated) == 'same':
            break
        else:
            schedule_original = deepcopy(schedule_updated)
            iteration += 1

        if save_log:
            naviio.schedule2xlsx(schedule_updated_order, fname='C-{}/I-{:04,d}_01-order.xlsx'.format(case_num, iteration), verbose=False)
            naviio.schedule2xlsx(schedule_updated_pre_dist, fname='C-{}/I-{:04,d}_02-pre_dist.xlsx'.format(case_num, iteration), verbose=False)
            naviio.schedule2xlsx(schedule_updated_productivity, fname='C-{}/I-{:04,d}_03-productivity.xlsx'.format(case_num, iteration), verbose=False)
            naviio.schedule2xlsx(schedule_updated_compressed, fname='C-{}/I-{:04,d}_04-compressed.xlsx'.format(case_num, iteration), verbose=False)
        else:
            pass

        end_time = time()
        iteration_time = end_time - start_time
        running_time += iteration_time
        times.append((iteration, iteration_time))
        print(' ({:.03f} sec/iter)'.format(iteration_time), end='')
        print(' (running: {:,d} sec)'.format(int(running_time)), end='')

    print('\n  | Running time: {:.03f} sec'.format(sum([t for _, t in times])))
    return schedule_updated


if __name__ == '__main__':
    ## Load project
    activity_book = naviio.import_activity_book()

    try:
        case_num = str(sys.argv[1])
    except:
        print('Insert project case number: ')
        sys.exit()

    schedule = import_schedule(case_num)
    schedule_normalized = normallize_duplicated_activity(schedule)

    ## Update schedule
    print('============================================================')
    print('Update schedule')
    schedule_updated = update(schedule_normalized, save_log=False)

    ## Export schedule
    try:
        naviio.schedule2xlsx(schedule=schedule_updated, fname='C-{}/updated.xlsx'.format(case_num))
    except:
        pass

    ## Print schedule
    navifunc.print_schedule(schedule=schedule_updated)