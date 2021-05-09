'''
A sourcecode to run the program and find the optimized schedule for the construction site.
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import json
import copy
import pandas as pd
from collections import defaultdict

import sys
sys.path.append('/data/blank54/workspace/project/navi/')
from object import Activity, Work, Project
from naviutil import NaviPath
navipath = NaviPath()


def assign_work_on_grid(case_data):
    current_grid = ''
    works = defaultdict(list)

    for idx, record in case_data.iterrows():
        if current_grid == record['grid']:
            day += 1
        else:
            current_grid = copy.deepcopy(record['grid'])
            day = 0

        name = record['activity_name']
        code = activity2code[record['activity_name']]
        productivity = activity2productivity[code]

        activity = Activity(code=code, name=name, productivity=productivity)
        works[current_grid].append(Work(grid=current_grid, activity=activity, day=day))
        
    return Project(works)

def workday_adjustment():
    global project

    for w2 in project.works['A2']:
        for w1 in project.works['A1']:
            if w1.activity.name == w2.activity.name:            
                if w2.day < w1.day:
                    w2.day = copy.deepcopy(w1.day)

    return project


if __name__ == '__main__':
    ## Load Templates
    with open(navipath.activity2code, 'r', encoding='utf-8') as f:
        activity2code = json.load(f)
    
    with open(navipath.activity2productivity, 'r', encoding='utf-8') as f:
        activity2productivity = json.load(f)


    ## Init Project
    case_data = pd.read_excel(navipath.case_01)
    project = assign_work_on_grid(case_data)


    ## Compare workday of activities
    for work in project.works['A1']:
        print('[{}]: /// {:<5} /// at day {}'.format(work.grid, work.activity.name, work.day))

    for work in project.works['A2']:
        print('[{}]: /// {:<5} /// at day {}'.format(work.grid, work.activity.name, work.day))


    ## Adjust workdays
    project_modi = workday_adjustment()

    for work in project_modi.works['A1']:
        print('[{}]: /// {:<5} /// at day {}'.format(work.grid, work.activity.name, work.day))

    for work in project_modi.works['A2']:
        print('[{}]: /// {:<5} /// at day {}'.format(work.grid, work.activity.name, work.day))