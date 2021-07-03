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


with open(navipath.navisystem, 'rb') as f:
    navisystem = pk.load(f)

if 'F20030' in navisystem.activities['S10040'].successor:
    print('F20030')