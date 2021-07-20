#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])

import pickle as pk

import sys
sys.path.append(rootpath)
from naviutil import NaviPath
navipath = NaviPath()


def load_project(case_num):
    with open(navipath.proj(case_num), 'rb') as f:
        return pk.load(f)

def do_reschedule(project):
    global case_num

    ## Export original schedule of the project.
    project.export(fpath=navipath.schedule(case_num))

    ## Reschedule the project and export the modified schedule.
    project.reschedule()
    project.export(fpath=navipath.reschedule(case_num))
    return project


if __name__ == '__main__':
    ## Project information
    case_num = '01'

    ## Reschedule the project
    project = load_project(case_num=case_num)
    project_modi = do_reschedule(project=project)

    ## Summary
    project_modi.summary(duration=True, sorted_grids=True)