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
def import_schedule(case_id):
    global activity_book

    try:
        fname_initial_schedule = 'C-{}.xlsx'.format(case_id)
        schedule = naviio.xlsx2schedule(activity_book=activity_book, fname=fname_initial_schedule)
        return schedule
    except FileNotFoundError:
        print('Error: You should run "init.py" first to build "C-{}.xlsx"'.format(case_id))
        sys.exit(1)

## Duplicated Activity Normalization
def normallize_duplicated_activity(schedule):
    global case_id

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

    fname = 'C-{}/normalized.xlsx'.format(case_id)
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

def activity_order_constraint(schedule, verbose_local=False, verbose_conflict=False):
    schedule_updated = deepcopy(schedule)

    iteration = 0
    for location in schedule.keys():
        local_schedule_original = deepcopy(schedule[location])

        while True:
            iteration += 1
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
                    distance = navifunc.euclidean_distance(current_location.split('_')[:2], comparing_location.split('_')[:2])
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
            elif existing_activity_code == activity_code:
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
def activity_productivity_constraint(schedule):
    global activity_book

    daily_work_plan = navifunc.build_daily_work_plan(schedule)
    schedule_updated = deepcopy(schedule)
    for day in sorted(daily_work_plan.keys(), reverse=False):
        activity_counter = defaultdict(list)
        for location, activity_code in daily_work_plan[day].items():
            activity_counter[activity_code].append(location)

        for activity_code, location_list in activity_counter.items():
            count = len(location_list)
            if navifunc.check_productivity_overload(activity_book, activity_code, count) == 'overloaded':
                num_overloaded = (count-activity_book[activity_code].productivity)
                for target_location in location_list[:num_overloaded]:
                    schedule_updated = deepcopy(push_workdays_single_location(schedule=schedule_updated, target_location=target_location, after=day))
            else:
                pass

    return schedule_updated


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
def update(schedule_original, do_order, do_pre_dist, do_productivity, do_compress, save_log):
    global case_id

    times = []
    iteration = 0
    running_time = 0
    schedule_updated = deepcopy(schedule_original)

    while True:
        print('\r  | Iteration: {:,d}'.format(iteration), end='')
        start_time = time()
        schedule_before = deepcopy(schedule_updated)
        
        ## Activity Order Constraint
        if do_order:
            schedule_updated = deepcopy(activity_order_constraint(schedule_updated, verbose_local=False, verbose_conflict=False))
            if save_log:
                naviio.schedule2xlsx(schedule_updated, fname='C-{}/I-{:04d}_01-order.xlsx'.format(case_id, iteration), verbose=False)
            else:
                pass
        else:
            pass

        ## Activity Predecessor Completion Constraint
        if do_pre_dist:
            schedule_updated = deepcopy(activity_predecessor_completion_constraint(schedule_updated))
            if save_log:
                naviio.schedule2xlsx(schedule_updated, fname='C-{}/I-{:04d}_02-pre_dist.xlsx'.format(case_id, iteration), verbose=False)
            else:
                pass
        else:
            pass

        ## Activity Productivity Constraint
        if do_productivity:
            schedule_updated = deepcopy(activity_productivity_constraint(schedule_updated))
            if save_log:
                naviio.schedule2xlsx(schedule_updated, fname='C-{}/I-{:04d}_03-productivity.xlsx'.format(case_id, iteration), verbose=False)
            else:
                pass
        else:
            pass

        ## Compress empty workday
        if do_compress:
            schedule_updated = deepcopy(compress_schedule(schedule_updated))
            if save_log:
                naviio.schedule2xlsx(schedule_updated, fname='C-{}/I-{:04d}_04-compressed.xlsx'.format(case_id, iteration), verbose=False)
            else:
                pass
        else:
            pass

        schedule_after = deepcopy(schedule_updated)
        if navifunc.compare_schedule(schedule_before, schedule_after) == 'same':
            break
        else:
            iteration += 1
            end_time = time()
            iteration_time = end_time - start_time
            running_time += iteration_time
            times.append((iteration, iteration_time))
            print(' (Running time: {:.03f} sec/iter & {:,d} sec/total)'.format(iteration_time, int(running_time)), end='')
            continue

    print('\n  | Total running time: {:.03f} sec'.format(sum([t for _, t in times])))
    return schedule_updated


if __name__ == '__main__':
    ## Load project
    activity_book = naviio.import_activity_book()

    try:
        case_id = str(sys.argv[1])
    except:
        print('Insert project case number: ')
        sys.exit()

    schedule = import_schedule(case_id)
    schedule_normalized = normallize_duplicated_activity(schedule)

    ## Update schedule
    print('============================================================')
    print('Update schedule')
    schedule_updated = update(schedule_original=schedule_normalized, 
                              do_order=True, 
                              do_pre_dist=True, 
                              do_productivity=True, 
                              do_compress=True,
                              save_log=True)

    ## Export schedule
    try:
        naviio.schedule2xlsx(schedule=schedule_updated, fname='C-{}/updated.xlsx'.format(case_id))
    except:
        pass

    ## Print schedule
    # navifunc.print_schedule(schedule=schedule_updated)