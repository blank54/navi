#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import pickle as pk

import sys
sys.path.append('/data/blank54/workspace/project/navi/')
from naviutil import NaviPath
navipath = NaviPath()


with open(navipath.navisystem, 'rb') as f:
    navisystem = pk.load(f)

navisystem.check_order()