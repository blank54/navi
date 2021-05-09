'''
A sourcecode to initialize the program.
It defines global variables and constraints.
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import json
import pandas as pd
from collections import defaultdict

import sys
sys.path.append('/data/blank54/workspace/project/navi/')
from naviutil import NaviPath
navipath = NaviPath()


def build_activity2code():
    activity2code = defaultdict(str)
    for idx, record in pd.read_excel(navipath.activity_list).iterrows():
        activity2code[str(record['name'])] = str(record['code'])
        
    with open(navipath.activity2code, 'w', encoding='utf-8') as f:
        json.dump(activity2code, f)

def build_activity2productivity():
    activity2productivity = defaultdict(str)
    for idx, record in pd.read_excel(navipath.productivity_list).iterrows():
        activity2productivity[str(record['code'])] = str(record['productivity'])
        
    with open(navipath.activity2productivity, 'w', encoding='utf-8') as f:
        json.dump(activity2productivity, f)


if __name__ == '__main__':
    build_activity2code()
    build_activity2productivity()