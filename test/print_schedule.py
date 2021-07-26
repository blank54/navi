## Print schedule#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import sys
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from naviutil import NaviPath
navipath = NaviPath()

import time
import numpy as np
import pickle as pk
from copy import deepcopy
from collections import defaultdict


def load_project(case_num):
    with open(navipath.proj(case_num), 'rb') as f:
        project = pk.load(f)

    return project

def assign_activity_to_grid(project):
    work_plan = defaultdict(list)
    for location in project.schedule:
        for activity_code, day in project.schedule[location].items():
            work_plan[day].append((location, activity_code))

    xs, ys, zs = [], [], []
    for location in project.schedule:
        x, y, z = location.split('_')
        xs.append(int(x))
        ys.append(int(y))
        zs.append(int(z))

    layout_format = np.chararray((max(xs), max(ys)), itemsize=6)
    layout_format[:] = '------'
    

    work_layout = {}
    for day in work_plan:
        daily_layout = {z: deepcopy(layout_format) for z in set(zs)}
        for location, activity_code in work_plan[day]:
            x, y, z = location.split('_')

            col = int(x)-1
            row = int(y)-1
            flr = int(z)

            daily_layout[flr][row, col] = activity_code

        work_layout[day] = daily_layout
        del daily_layout

    return work_layout

def print_work_layout(work_layout, timesleep=1):
    for day in sorted(work_layout.keys(), reverse=False):
        print('\n\n\n\n============================================================')
        print('Work Layout: (Day: {})'.format(day))

        time.sleep(timesleep)
        for flr in sorted(work_layout[day].keys(), reverse=False):
            print('--------------------------------------------------')
            print('Floor: {}'.format(flr))
            print(work_layout[day][flr])


if __name__ == '__main__':
    ## Load project
    case_num = '03_updated'
    project = load_project(case_num=case_num)

    ## Print by grid
    work_layout = assign_activity_to_grid(project)
    print_work_layout(work_layout)