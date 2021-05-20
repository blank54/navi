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
from object import Work, Grid, Project
from naviutil import NaviPath
navipath = NaviPath()


def load_activity_tree():
    with open(navipath.activity_tree, 'rb') as f:
        return pk.load(f)

def initiate_project():
    case_data = pd.read_excel(navipath.case_01)
    activity_tree = load_activity_tree()
    grids = defaultdict(Grid)

    for idx, line in case_data.iterrows():
        x = int(line['x'])
        y = int(line['y'])
        z = int(line['z'])
        location = '{}_{}_{}'.format(x, y, z)
        grid = Grid(location=location)

        try:
            code = line['code']
            activity = activity_tree.leaves[code]
        except KeyError:
            continue

        if location in grids:
            grid = grids[location]
            today = grid.last_day+1
        else:
            grid = Grid(location=location)
            today = 0

        grid.works.append(Work(activity=activity, day=today))
        grid.update()
        grids[location] = grid

    return Project(grids=grids)


if __name__ == '__main__':
    ## Init Project
    project = initiate_project()
    project.summary()
    project.export(fpath=navipath.case_01_proj)




    ## Adjust workdays
    project_modi = deepcopy(project)
    project_modi.adjust_all()
    project_modi.update()
    project_modi.summary()
    project.export(fpath=os.path.join(navipath.fdir_data, 'case_01_proj_modi.xlsx'))