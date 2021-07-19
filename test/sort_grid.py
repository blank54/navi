#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import sys
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from naviutil import NaviPath
navipath = NaviPath()

import numpy as np
import pickle as pk
from copy import deepcopy
from collections import defaultdict


def load_project(case_num):
    with open(navipath.proj(case_num), 'rb') as f:
        return pk.load(f)

def euclidean_distance(x, y):
    x_arr = np.array(x)
    y_arr = np.array(y)
    dist = np.linalg.norm(y_arr-x_arr)
    return dist

def sort_grids(project):
    sorted_by_work_len = sorted(project.grids, key=lambda x:len(x.works), reverse=True)

    worklen2grid = defaultdict(list)
    for grid in sorted_by_work_len:
        worklen2grid[len(grid.works)].append(grid)


    sorted_by_dist = []
    for worklen, grids_same_worklen in sorted(worklen2grid.items(), key=lambda x:x[0], reverse=True):
        print('============================================================')
        print('Work length: {}'.format(worklen))
        print('Grids:', [grid.location_3d for grid in grids_same_worklen])

        while len(grids_same_worklen) > 0:
            try:
                last_grid = sorted_by_dist[-1]
            except IndexError:
                last_grid = grids_same_worklen[0]

            grids_same_worklen = sorted(grids_same_worklen, key=lambda x:euclidean_distance(x.location_3d, last_grid.location_3d), reverse=False)
            print('  ----------------------------------------')
            print('  | Last grid : {}'.format(last_grid.location_3d))
            print('  | Most close: {} (dist: {:.03f})'.format(grids_same_worklen[0].location_3d, euclidean_distance(last_grid.location_3d, grids_same_worklen[0].location_3d)))
            sorted_by_dist.append(grids_same_worklen[0])
            grids_same_worklen.pop(0)

    for grid in sorted_by_dist:
        print('{}: {}'.format(grid.location_3d, len(grid.works)))


if __name__ == '__main__':
    ## Load project
    case_num = '01'
    project = load_project(case_num=case_num)


    ## Sort grids
    # sort_grids(project=project)
    project.summary(sorted_grids=True)