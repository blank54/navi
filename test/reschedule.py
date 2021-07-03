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

def do_reschedule():
    with open(navipath.case_01_proj, 'rb') as f:
        project = pk.load(f)

    ## Export original schedule of the project.
    project.export(fpath=navipath.case_01_schedule)

    ## Reschedule the project.
    project.reschedule()

    ## Export modified schedule of the project.
    project.export(fpath=navipath.case_01_reschedule)


if __name__ == '__main__':
    do_reschedule()