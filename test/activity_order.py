#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import pickle as pk

import sys
sys.path.append('/data/blank54/workspace/project/navi/')
from naviutil import NaviPath
navipath = NaviPath()


with open(navipath.activity_tree, 'rb') as f:
    tree = pk.load(f)

tree.check_order()