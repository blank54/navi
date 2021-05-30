'''
A sourcecode to initialize the program.
It defines global variables and constraints.
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import pickle as pk
import pandas as pd
from copy import deepcopy
from collections import defaultdict

import sys
sys.path.append('/data/blank54/workspace/project/navi/')
from object import Activity, NaviSystem
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
        prod = line['productivity']

        parameters = {
            'category': category,
            'major': major,
            'minor': minor,
            'code': code,
            'prod': prod,
        }
        activities[code] = Activity(parameters=parameters)

    return NaviSystem(activities=activities)

def save_navisystem(navisystem):
    with open(navipath.navisystem, 'wb') as f:
        pk.dump(navisystem, f)

    print('Save NaviSystem:')
    print('  | FilePath: {}'.format(navipath.navisystem))
    print('  | # of Activities: {}'.format(len(navisystem)))

def set_activity_order(navisystem):
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

    if key_errors:
        key_errors = list(set(key_errors))
        for code in key_errors:
            print('Absent in ActivityTable: {}'.format(code))
    else:
        pass

    return navisystem


if __name__ == '__main__':
    navisystem = set_navisystem()
    navisystem_ordered = set_activity_order(navisystem=navisystem)
    save_navisystem(navisystem=navisystem_ordered)