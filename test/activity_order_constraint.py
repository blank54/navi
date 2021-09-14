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


def import_schedule(fname):
    global activity_book

    schedule = navifunc.xlsx2schedule(activity_book=activity_book, fname=fname)
    normalized_schedule = normallize_duplicated_activity(schedule)
    return normalized_schedule

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

def update_order_in_local_schedule(local_schedule, verbose=False):
    for day, activity_code in sorted(local_schedule.items(), key=lambda x:x[0]):
        conflict_items = check_activity_order_within_work(local_schedule, activity_code)
        
        if verbose:
            print('{:2}: {}'.format(day, activity_code))
        else:
            pass

        if conflict_items:
            for conflicted_day, conflicted_activity_code in conflict_items:
                print('  | Conflicts at {}({}) <-> {}({})'.format(activity_code, day, conflicted_activity_code, conflicted_day))

            local_schedule_updated = deepcopy(reorder_activity(local_schedule, activity_code, conflict_items))
            return local_schedule_updated
        else:
            continue

    return local_schedule

def update_order(schedule, verbose_iter=False, verbose_local=False):
    schedule_updated = defaultdict(dict)

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

            local_schedule_updated = deepcopy(update_order_in_local_schedule(local_schedule=local_schedule_original, verbose=verbose_local))
            if navifunc.compare_local_schedule(local_schedule_original, local_schedule_updated) == 'same':
                schedule_updated[location] = deepcopy(local_schedule_updated)
                break
            else:
                local_schedule_original = deepcopy(local_schedule_updated)

    return schedule_updated


if __name__ == '__main__':
    fname_activity_book = 'activity_book.pk'
    with open(os.path.sep.join(navipath.fdir_component, fname_activity_book), 'rb') as f:
        activity_book = pk.load(f)

    case_num = '01'
    fname_schedule_original = os.path.sep.join(navipath.fdir_schedule, 'C-{}.xlsx'.format(case_num))
    schedule_original = import_schedule(fname=fname_schedule_original)
    schedule_updated = update_order(schedule=schedule_original, verbose_iter=True, verbose_local=False)