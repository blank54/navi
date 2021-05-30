#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
A sourcecode to run the program and find the optimized schedule for the construction site.
'''

# Configuration
import os
import pickle as pk
import pandas as pd
from copy import deepcopy
from collections import defaultdict

import sys
sys.path.append('/data/blank54/workspace/project/navi/')
from object import Grid, Project
from naviutil import NaviPath
navipath = NaviPath()


def load_navisystem():
    with open(navipath.navisystem, 'rb') as f:
        return pk.load(f)

def define_works():
    case_data = pd.read_excel(navipath.case_01)
    navisystem = load_navisystem()


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

def initiate_project():
    global works, duration

    grids = []
    for loc in works:
        grids.append(Grid(location=loc, works=works[loc]))

    project = Project(grids=grids, duration=duration)
    # project.summary()
    project.export(fpath=navipath.case_01_proj)

    return project

def adjust_project():
    global project

    # project.find(activity_code='S10020', verbose=True)
    project.push_workday(location='2_3_2', start_day=1, change=1)
    project.export(fpath=navipath.case_01_proj_test)


if __name__ == '__main__':
    ## Init Project
    duration = 60
    works = define_works()

    project = initiate_project()
    adjust_project()