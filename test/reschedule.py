#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import pickle as pk

import sys
sys.path.append('/data/blank54/workspace/project/navi/')
from naviutil import NaviPath
navipath = NaviPath()

def do_reschedule():
    with open(navipath.case_01_proj, 'rb') as f:
        project = pk.load(f)

    # project.reschedule_oneday_oneactivity()
    # project.reschedule_push_and_pull()
    project.reschedule()
    project.export(fpath=navipath.case_01_reschedule)


if __name__ == '__main__':
    do_reschedule()