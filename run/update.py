#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import sys
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from naviutil import NaviPath, NaviFunc
navipath = NaviPath()
navifunc = NaviFunc()

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
        schedule = navifunc.xlsx2schedule(activity_book=activity_book, fname=fname_initial_schedule)
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
    navifunc.schedule2xlsx(schedule_normalized, fname, verbose=False)
    return schedule_normalized

## Activity Order Constraint
def check_activity_order_within_work(local_schedule, activity_code):
    global activit_book

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


## Activity Productivity Constraint
def check_productivity_overload(activity_code, count):
    try:
        if count > activity_book[activity_code].productivity:
            return 'overloaded'
        else:
            return 'fine'
    except KeyError:
        return 'fine'

def push_workdays_uniformly(schedule, target_location, after):
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
            schedule_updated[location][after] = ''
    return schedule_updated

def activity_productivity_constraint(schedule, daily_work_plan):
    global activity_book

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
                    schedule_updated = deepcopy(push_workdays_uniformly(schedule=schedule, target_location=target_location, after=day))
            else:
                continue

    if schedule_updated:
        return schedule_updated
    else:
        return schedule

# 생산성은 동일레벨(Z값이 동일 그리드끼리만)계산
# Z값이 다를 경우 다른 일정으로 진행
# 현재는 1개 팀으로 운영기준
# 전체기간 내 완료가 불가능할 경우, 팀의 수를 늘려야하며,
# 각 작업팀이 Z값이 다른 그리드에서 작업하도록 하거나 동일한 Z내에서 거리가 먼 영역을 작업하도록 함.

### Activity Predecessor Completion Constraint
# def check_activity_dis(activity_code):
#     for day, works, location in ????: #

# # import updated schedule
# 날짜, 그리드, 작업, 작업선행완료 거리값으로 디셔너리 생성
# 그리드와 작업선행완료 거리값이 해당되는 그리드값 생성
# # 작업별 순서 절대값 비교


# def check_activity_type(activity_code):
#     if activity_code[0] == "d":
#         #activiy code가 d로 시작하면 위에서 아래로, 그리드 z값이 1씩 줄어드는 순서로 작업한다
#         #선행완료 거리 제약에 1,1,-2는 *,*,-1의 거리 범위에 선행작업이 완료되어야 작업가능
#         # excavation

#         return .....
#     elif activity_code[0] == "s":
#         #activiy code가 s로 시작하면 위에서 아래로, 그리드 z값이 1씩 늘어나는 순서로 작업한다
#         #선행완료 거리 제약에 1,1,-1는 *,*,-2의 거리 범위에 선행작업이 완료되어야 작업가능
#         # structure
#         return .....
#     elif activity_code[0] == "m":
#         #activiy code가 m로 시작하면 z값을 무시 작업한다
#         # milestone
#         return .....
#     else:
#         #activiy code가 s나 d가 아니면
#         #선행완료 거리 제약에 1,1,-1는 *,*,-1의 거리 범위에 선행작업이 완료되어야 작업가능 (동일 레벨만 고려하고)
#         #동일 레벨에서 생산성을 반영
#         return 'fine'

# #작업이 선행작업


## Update schedule
def update(schedule_original, save_log=True):
    times = []
    iteration = 0
    while True:
        print('\r  | Iteration: {:03,d}'.format(iteration), end='')
        start_time = time()
        
        ## Work Plans
        daily_work_plan = navifunc.build_daily_work_plan(schedule_original)

        ## Activity Order Constraint
        schedule_updated_order = deepcopy(activity_order_constraint(schedule_original, verbose_iter=False, verbose_local=False, verbose_conflict=False))

        ## Activity Predecessor Completion Constraint
        # schedule_updated = deepcopy(activity_predecessor_completion_constraint(schedule_updated))

        ## Activity Productivity Constraint
        schedule_updated_productivity = deepcopy(activity_productivity_constraint(schedule_updated_order, daily_work_plan))

        schedule_updated = deepcopy(schedule_updated_productivity)
        if navifunc.compare_schedule(schedule_original, schedule_updated) == 'same':
            break
        else:
            schedule_original = deepcopy(schedule_updated)
            iteration += 1

        if save_log:
            navifunc.schedule2xlsx(schedule_updated_order, fname='C-{}/I-{:03,d}_01-order.xlsx'.format(case_num, iteration), verbose=False)
            navifunc.schedule2xlsx(schedule_updated_productivity, fname='C-{}/I-{:03,d}_02-productivity.xlsx'.format(case_num, iteration), verbose=False)
        else:
            pass

        end_time = time()
        running_time = end_time - start_time
        times.append((iteration, running_time))
        print(' ({:.03f} sec)'.format(running_time), end='')

    print('\n  | Running time: {:,d} sec'.format(sum([t for _, t in times])))
    return schedule_updated


if __name__ == '__main__':
    try:
        fname_activity_book = 'activity_book.pk'
        with open(os.path.sep.join((navipath.fdir_component, fname_activity_book)), 'rb') as f:
            activity_book = pk.load(f)
    except FileNotFoundError:
        print('Error: You should run "init.py" first to build "activity_book.pk"')
        sys.exit(1)

    case_num = '01'
    schedule = import_schedule(case_num)
    schedule_normalized = normallize_duplicated_activity(schedule)

    ## Update schedule
    print('============================================================')
    print('Update schedule')
    schedule_updated = update(schedule_normalized, save_log=True)

    ## Print schedule
    # navifunc.print_schedule(schedule=schedule_updated)