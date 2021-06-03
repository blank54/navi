#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import pickle as pk

import sys
sys.path.append('/data/blank54/workspace/project/navi/')
from naviutil import NaviPath
navipath = NaviPath()


with open(navipath.case_01_proj, 'rb') as f:
    project = pk.load(f)

project.reschedule()
project.export(fpath=navipath.case_01_reschedule)