#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
A sourcecode to run the program and find the optimized schedule for the construction site.
'''

# Configuration
import pickle as pk
import pandas as pd
from copy import deepcopy
from collections import defaultdict

import sys
sys.path.append('/data/blank54/workspace/project/navi/')
from object import Work, Project
from naviutil import NaviPath
navipath = NaviPath()


def load_activity_tree():
    with open(navipath.activity_tree, 'rb') as f:
        return pk.load(f)

def initiate_project():
    case_data = pd.read_excel(navipath.case_01)
    activity_tree = load_activity_tree()

    current_grid = ''
    works = defaultdict(list)
    for idx, line in case_data.iterrows():
        if current_grid == line['grid']:
            day += 1
        else:
            current_grid = deepcopy(line['grid'])
            day = 0

        name = line['activity_name']
        activity = activity_tree.leaves[name]

        works[current_grid].append(Work(grid=current_grid, activity=activity, day=day))
        
    return Project(works=works)


if __name__ == '__main__':
    ## Init Project
    project = initiate_project()


    ## Compare workday of activities
    for work in project.works['A1']:
        print('[{}]: /// {:<5} /// at day {}'.format(work.grid, work.activity.name, work.day))

    for work in project.works['A2']:
        print('[{}]: /// {:<5} /// at day {}'.format(work.grid, work.activity.name, work.day))


    ## Adjust workdays
    project.find_critical_grid()
    project.adjust_one('A2')

    for work in project.works['A1']:
        print('[{}]: /// {:<5} /// at day {}'.format(work.grid, work.activity.name, work.day))

    for work in project.works['A2']:
        print('[{}]: /// {:<5} /// at day {}'.format(work.grid, work.activity.name, work.day))