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


def do_reschedule(case_num):
    with open(navipath.proj(case_num), 'rb') as f:
        project = pk.load(f)

    ## Export original schedule of the project.
    project.export(fpath=navipath.schedule(case_num))

    ## Reschedule the project.
    project.reschedule()

    ## Export modified schedule of the project.
    project.export(fpath=navipath.reschedule(case_num))


if __name__ == '__main__':
    ## Project information
    case_num = '01'

    ## Reschedule the project
    do_reschedule(case_num)