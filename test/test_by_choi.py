#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Configuration
import os
import sys

#__file__ = os.getcwd()

rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from naviutil import NaviPath, NaviFunc, NaviIO
navipath = NaviPath()
navifunc = NaviFunc()
naviio = NaviIO()

import shutil
import itertools
from time import time
import pandas as pd
import pickle as pk
from copy import deepcopy
from collections import defaultdict, Counter


## Data Import
def import_schedule(case_num):
    global activity_book

    try:
        fname_initial_schedule = 'C-{}.xlsx'.format(case_num)
        schedule = naviio.xlsx2schedule(activity_book=activity_book, fname=fname_initial_schedule)
        return schedule
    except FileNotFoundError:
        print('Error: You should run "init.py" first to build "C-{}.xlsx"'.format(case_num))
        sys.exit(1)

activity_book
