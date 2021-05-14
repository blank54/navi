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
from object import Work, Grid, Project
from naviutil import NaviPath
navipath = NaviPath()


def load_activity_tree():
    with open(navipath.activity_tree, 'rb') as f:
        return pk.load(f)

def initiate_project():
    case_data = pd.read_excel(navipath.case_01)
    activity_tree = load_activity_tree()

    work_list_on_location = defaultdict(list)
    current_location = ''
    for idx, line in case_data.iterrows():
        if current_location != line['location']:
            current_location = deepcopy(line['location'])
            day = 0
        else:
            day += 1

        name = line['activity_name']
        activity = activity_tree.leaves[name]
        
        work = Work(location=current_location, activity=activity, day=day)
        work_list_on_location[current_location].append(work)

    grids = defaultdict()
    for location in work_list_on_location.keys():
        grids[location] = Grid(location=location, works=work_list_on_location[location])

    return Project(grids=grids)


if __name__ == '__main__':
    ## Init Project
    project = initiate_project()
    project.summary()


    ## Adjust workdays
    project_modi = deepcopy(project)
    project_modi.adjust_all()
    project_modi.update()
    project_modi.summary()