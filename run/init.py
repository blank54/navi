'''
A sourcecode to initialize the program.
It defines global variables and constraints.
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])

import pickle as pk
import pandas as pd
from copy import deepcopy
from collections import defaultdict

import sys
sys.path.append(rootpath)
from object import NaviSystem, Activity, Grid, Project
from naviutil import NaviPath
navipath = NaviPath()


def set_navisystem():
    activity_table = pd.read_excel(navipath.activity_table)
    activities = {}
    for _, line in activity_table.iterrows():
        category = line['category']
        major = line['major_activity']
        minor = line['minor_activity']
        code = line['code']
        productivity = line['productivity']

        parameters = {
            'category': category,
            'major': major,
            'minor': minor,
            'code': code,
            'productivity': productivity,
        }
        activities[code] = Activity(parameters=parameters)

    return NaviSystem(activities=activities)

def init_activity_order(navisystem):
    activity_order = pd.read_excel(navipath.activity_order)
    key_errors = []
    for _, line in activity_order.iterrows():
        predecessor_code = line['predecessor']
        successor_code = line['successor']

        try:
            predecessor_activity = deepcopy(navisystem.activities[predecessor_code])
        except KeyError:
            key_errors.append(predecessor_code)
            continue
        try:
            successor_activity = deepcopy(navisystem.activities[successor_code])
        except KeyError:
            key_errors.append(successor_code)
            continue

        predecessor_activity.add_successor(successor_activity.code)
        successor_activity.add_predecessor(predecessor_activity.code)

        navisystem.activities[predecessor_code] = predecessor_activity
        navisystem.activities[successor_code] = successor_activity

    print('==================================================')
    print('Errors on Activities')
    if key_errors:
        key_errors = list(set(key_errors))
        for code in key_errors:
            print('  | Absent in NaviSystem: {}'.format(code))
    else:
        pass

    return navisystem

def set_activity_order_recursively(navisystem):
    navisystem = init_activity_order(navisystem)

    updates = [True]
    while any(updates) == True:
        updates = []
        for activity_code in navisystem.activities:
            activity = navisystem.activities[activity_code]

            existing_preds = deepcopy(list(set(activity.predecessor)))
            for pred_code in activity.predecessor:
                pred_of_pred = list(set(navisystem.activities[pred_code].predecessor))
                updated_preds = deepcopy(list(set(existing_preds+pred_of_pred)))
                if set(updated_preds) != set(existing_preds):
                    navisystem.activities[activity_code].predecessor = updated_preds
                    updates.append(True)
            
            existing_succs = deepcopy(list(set(activity.successor)))
            for succ_code in activity.successor:
                succ_of_succ = list(set(navisystem.activities[succ_code].successor))
                updated_succs = deepcopy(list(set(existing_succs+succ_of_succ)))
                if set(updated_succs) != set(existing_succs):
                    navisystem.activities[activity_code].successor = updated_succs
                    updates.append(True)

    return navisystem

def save_navisystem(navisystem):
    os.makedirs(navipath.fdir_component, exist_ok=True)
    with open(navipath.navisystem, 'wb') as f:
        pk.dump(navisystem, f)

    print('==================================================')
    print('Save NaviSystem:')
    print('  | FilePath: {}'.format(navipath.navisystem))
    print('  | # of Activities: {}'.format(len(navisystem)))

def load_navisystem():
    with open(navipath.navisystem, 'rb') as f:
        navisystem = pk.load(f)
    return navisystem

def define_works(navisystem, case_data):
    works = defaultdict(list)
    for idx, line in case_data.iterrows():
        x = int(line['x'])
        y = int(line['y'])
        z = int(line['z'])
        location = '{}_{}_{}'.format(x, y, z)

        try:
            code = line['code']
            activity = navisystem.activities[code]
        except KeyError:
            continue

        works[location].append(activity)

    return works

def initiate_project(case_num, duration):
    navisystem = load_navisystem()

    print('==================================================')
    print('Init Project')

    case_data = pd.read_excel(navipath.case(case_num))
    works = define_works(navisystem, case_data)
    grids = []
    for loc in works:
        grids.append(Grid(location=loc, works=works[loc]))

    project = Project(activities=navisystem.activities, grids=grids, duration=duration)
    project.summary()

    return project

def save_project(case_num, project):
    os.makedirs(navipath.fdir_proj, exist_ok=True)
    with open(navipath.proj(case_num), 'wb') as f:
        pk.dump(project, f)

    print('==================================================')
    print('Save Project:')
    print('  | FilePath: {}'.format(navipath.proj(case_num)))


if __name__ == '__main__':
    ## Init NaviSystem
    navisystem = set_navisystem()
    navisystem_ordered = set_activity_order_recursively(navisystem=navisystem)
    save_navisystem(navisystem=navisystem_ordered)

    ## Project Constraints
    case_num = '01'
    duration = 60
    
    ## Init Project
    project = initiate_project(case_num, duration)
    save_project(case_num, project)