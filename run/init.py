'''
A sourcecode to initialize the program.
It defines global variables and constraints.
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import sys
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from object import Activity, Grid, Project
from naviutil import NaviPath, NaviFunc, NaviIO
navipath = NaviPath()
navifunc = NaviFunc()
naviio = NaviIO()

import pickle as pk
import pandas as pd
from copy import deepcopy
from collections import defaultdict


def init_activity_book():
    global fname_activity_book

    activity_table = pd.read_excel(navipath.activity_table)
    acti

    activity_book = {}
    for _, line in activity_table.iterrows():
        category = line['category']
        major = line['major_activity']
        minor = line['minor_activity']
        code = line['code']
        productivity = line['productivity']
        pre_dist = line['pre_dist']

        parameters = {
            'category': category,
            'major': major,
            'minor': minor,
            'code': code,
            'productivity': productivity,
            'pre_dist': pre_dist,
        }
        activity_book[code] = Activity(parameters=parameters)

    os.makedirs(navipath.fdir_component, exist_ok=True)
    with open(os.path.sep.join((navipath.fdir_component, fname_activity_book)), 'wb') as f:
        pk.dump(activity_book, f)

    print('============================================================')
    print('Init ActivityBook')
    print('  | fdir : {}'.format(navipath.fdir_component))
    print('  | fname: {}'.format(fname_activity_book))

def set_orders_in_activity_book():
    global fname_activity_book

    with open(os.path.sep.join((navipath.fdir_component, fname_activity_book)), 'rb') as f:
        activity_book = pk.load(f)

    activity_order = pd.read_excel(navipath.activity_order)
    key_errors = []
    for _, line in activity_order.iterrows():
        predecessor_code = line['predecessor']
        successor_code = line['successor']

        try:
            predecessor_activity = deepcopy(activity_book[predecessor_code])
        except KeyError:
            key_errors.append(predecessor_code)
            continue
        try:
            successor_activity = deepcopy(activity_book[successor_code])
        except KeyError:
            key_errors.append(successor_code)
            continue

        predecessor_activity.add_successor(successor_activity.code)
        successor_activity.add_predecessor(predecessor_activity.code)

        activity_book[predecessor_code] = predecessor_activity
        activity_book[successor_code] = successor_activity

    updates = [True]
    while any(updates) == True:
        updates = []
        for activity_code in activity_book:
            activity = activity_book[activity_code]

            existing_preds = deepcopy(list(set(activity.predecessor)))
            for pred_code in activity.predecessor:
                pred_of_pred = list(set(activity_book[pred_code].predecessor))
                updated_preds = deepcopy(list(set(existing_preds+pred_of_pred)))
                if set(updated_preds) != set(existing_preds):
                    activity_book[activity_code].predecessor = updated_preds
                    updates.append(True)
            
            existing_succs = deepcopy(list(set(activity.successor)))
            for succ_code in activity.successor:
                succ_of_succ = list(set(activity_book[succ_code].successor))
                updated_succs = deepcopy(list(set(existing_succs+succ_of_succ)))
                if set(updated_succs) != set(existing_succs):
                    activity_book[activity_code].successor = updated_succs
                    updates.append(True)

    with open(os.path.sep.join((navipath.fdir_component, fname_activity_book)), 'wb') as f:
        pk.dump(activity_book, f)

    print('============================================================')
    print('Set order information to ActivityBook')
    print('  | fdir : {}'.format(navipath.fdir_component))
    print('  | fname: {}'.format(fname_activity_book))

    if key_errors:
        print('Errors on ActivityOrder template')
        key_errors = list(set(key_errors))
        for activity_code in key_errors:
            print('  | Absent in ActivityBook: {}'.format(activity_code))
    else:
        pass

def define_works(case_num):
    global fname_activity_book

    with open(os.path.sep.join((navipath.fdir_component, fname_activity_book)), 'rb') as f:
        activity_book = pk.load(f)

    case_data = pd.read_excel(navipath.case(case_num))
    works = defaultdict(list)
    for idx, line in case_data.iterrows():
        x = int(line['x'])
        y = int(line['y'])
        z = int(line['z'])
        location = '{}_{}_{}'.format(x, y, z)

        try:
            activity_code = line['code']
            activity = activity_book[activity_code]
        except KeyError:
            continue

        works[location].append(activity)

    return works

def initiate_project(case_num, duration):
    works = define_works(case_num)
    grids = []
    for loc in works:
        grids.append(Grid(location=loc, works=works[loc]))

    project = Project(grids=grids, duration=duration)
    project.summary()

    os.makedirs(navipath.fdir_proj, exist_ok=True)
    with open(navipath.proj(case_num), 'wb') as f:
        pk.dump(project, f)

    print('============================================================')
    print('Init Project')
    print('  | fdir : {}'.format(navipath.fdir_proj))
    print('  | fname: {}'.format(os.path.basename(navipath.proj(case_num))))

def export_initial_schedule(case_num):
    with open(navipath.proj(case_num), 'rb') as f:
        project = pk.load(f)

    fname_schedule = 'C-{}.xlsx'.format(case_num)
    schedule = navifunc.grids2schedule(grids=project.sorted_grids)
    naviio.schedule2xlsx(schedule=schedule, fname=fname_schedule)

if __name__ == '__main__':
    ## Project Constraints
    fname_activity_book = 'activity_book.pk'
    case_num = '003'
    duration = 15

    ## Activity Book
    init_activity_book()
    set_orders_in_activity_book()

    ## Project
    define_works(case_num)
    initiate_project(case_num, duration)

    ## Schedule
    export_initial_schedule(case_num)