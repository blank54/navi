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
from object import Activity, ActivityTree
from naviutil import NaviPath
navipath = NaviPath()


def set_activity_tree():
    activity_table = pd.read_excel(navipath.activity_table)
    leaves = {}
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
        leaves[code] = Activity(parameters=parameters)

    return ActivityTree(leaves=leaves)

def save_activity_tree(tree):
    with open(navipath.activity_tree, 'wb') as f:
        pk.dump(tree, f)

    print('Save ActivityTree:')
    print('  | FilePath: {}'.format(navipath.activity_tree))
    print('  | # of Activities: {}'.format(len(tree)))

def set_activity_order(tree):
    activity_order = pd.read_excel(navipath.activity_order)
    key_errors = []
    for _, line in activity_order.iterrows():
        predecessor_code = line['predecessor']
        successor_code = line['successor']

        try:
            predecessor_activity = deepcopy(tree.leaves[predecessor_code])
        except KeyError:
            key_errors.append(predecessor_code)
            continue
        try:
            successor_activity = deepcopy(tree.leaves[successor_code])
        except KeyError:
            key_errors.append(successor_code)
            continue

        predecessor_activity.add_successor(successor_activity)
        successor_activity.add_predecessor(predecessor_activity)

        tree.leaves[predecessor_code] = predecessor_activity
        tree.leaves[successor_code] = successor_activity

    if key_errors:
        key_errors = list(set(key_errors))
        for code in key_errors:
            print('Absent in ActivityTable: {}'.format(code))
    else:
        pass

    return tree


if __name__ == '__main__':
    activity_tree = set_activity_tree()
    activity_tree_ordered = set_activity_order(tree=activity_tree)
    save_activity_tree(tree=activity_tree_ordered)