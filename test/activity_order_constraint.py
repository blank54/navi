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

from copy import deepcopy
import pickle as pk
from collections import defaultdict


def normallize_duplicated_activity(schedule):
    normalized_schedule = defaultdict(dict)

    for location in schedule:
        normalized_schedule[location] = {}

        day = 0
        for activity_code in schedule[location].values():
            if activity_code not in normalized_schedule[location].values():
                normalized_schedule[location][day] = activity_code
                day += 1
            else:
                continue

    return normalized_schedule

def check_activity_order_within_work(local_schedule, activity_code):
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

    # print(current)
    # print(move_to)

    for day in range(0, len(local_schedule), 1):
        if day < current or day > move_to:
            # print('irrelevant: {}'.format(day))
            local_schedule_updated[day] = local_schedule[day]
        elif day == current:
            local_schedule_updated[move_to] = local_schedule[day]
            # print('reorder this: {}'.format(day))
        else:
            local_schedule_updated[day-1] = local_schedule[day]
            # print('pull these: {}'.format(day))

    return {d: a for d, a in sorted(local_schedule_updated.items(), key=lambda x:x[0])}
    # for day, activity_code in sorted(local_schedule_updated.items(), key=lambda x:x[0]):
    #     print('{:2}: {}'.format(day, activity_code))

def update_order_in_local_schedule(local_schedule):
    for day, activity_code in sorted(local_schedule.items(), key=lambda x:x[0]):
        conflict_items = check_activity_order_within_work(local_schedule, activity_code)
        
        print('{:2}: {}'.format(day, activity_code))
        if conflict_items:
            print('============================================================')
            for day, activity_code2 in conflict_items:
                print('  | Conflicts at {}: {}'.format(day, activity_code2))
            # print('============================================================')

            local_schedule_updated = deepcopy(reorder_activity(local_schedule, activity_code, conflict_items))
            return local_schedule_updated
        else:
            continue

    return local_schedule



# def check_activity_order_on_single_location(schedule, location):
#     global activity_book

#     results = []

#     for activity_code1, activity_code2 in itertools.combinations(schedule[location].values(), r=2):
#         try:
#             activity_1 = activity_book[activity_code1]
#             activity_2 = activity_book[activity_code2]
#         except KeyError:
#             continue

#         if activity_code2 in activity_1.successor:
#             results.append('fine')
#         elif activity_code2 in activity_1.predecessor:
#             results.append('conflict')
#         else:
#             results.append('irrelevant')



if __name__ == '__main__':
    fname_activity_book = 'activity_book.pk'
    with open(os.path.join(navipath.fdir_component, fname_activity_book), 'rb') as f:
        activity_book = pk.load(f)

    case_num = '01'
    fname_initial_schedule = os.path.join(navipath.fdir_schedule, 'C-{}.xlsx'.format(case_num))
    schedule = navifunc.xlsx2schedule(activity_book=activity_book, fname=fname_initial_schedule)
    normalized_schedule = normallize_duplicated_activity(schedule)

    iteration = 0
    local_schedule_original = deepcopy(normalized_schedule['2_1_1'])
    while True:
        print('Iteration: {:03,d}'.format(iteration))
        local_schedule_updated = deepcopy(update_order_in_local_schedule(local_schedule_original))

        print(local_schedule_updated)

        if navifunc.compare_local_schedule(local_schedule_original, local_schedule_updated) == 'same':
            break
        else:
            local_schedule_original = deepcopy(local_schedule_updated)
            iteration += 1