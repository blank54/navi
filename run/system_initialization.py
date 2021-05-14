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
        name = line['name']
        code = line['code']
        prod = line['productivity']
        leaves[name] = Activity(name=name, code=code, prod=prod)

    return ActivityTree(leaves=leaves)

def save_activity_tree(tree):
    with open(navipath.activity_tree, 'wb') as f:
        pk.dump(tree, f)

    print('Save ActivityTree:')
    print('  | /// {} ///'.format(navipath.activity_tree))

def set_activity_order(tree):
    activity_order = pd.read_excel(navipath.activity_order)
    for _, line in activity_order.iterrows():
        previous_name = line['previous']
        next_name = line['next']

        previous_activity = deepcopy(tree.leaves[previous_name])
        next_activity = deepcopy(tree.leaves[next_name])

        previous_activity.add_next(next_activity)
        next_activity.add_previous(previous_activity)

        tree.leaves[previous_name] = previous_activity
        tree.leaves[next_name] = next_activity

    return tree


if __name__ == '__main__':
    activity_tree = set_activity_tree()
    activity_tree_ordered = set_activity_order(tree=activity_tree)
    save_activity_tree(tree=activity_tree_ordered)