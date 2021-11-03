#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Configuration
import os
import sys
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from naviutil import NaviPath, NaviFunc, NaviIO
navipath = NaviPath()
navifunc = NaviFunc()
naviio = NaviIO()

import time


if __name__ == '__main__':
    ## Load project
    activity_book = naviio.import_activity_book()

    try:
        case_id = str(sys.argv[1])
    except:
        print('Insert project case number: ')
        sys.exit()

    fdir = os.path.sep.join((navipath.fdir_schedule, 'C-{}'.format(case_id)))
    flist = [fname for fname in os.listdir(fdir) if fname.startswith('I')]

    for fname in sorted(flist):
        iteration_part, constraint_part = fname.replace('.xlsx', '').split('_')
        iteration = iteration_part.split('-')[-1]
        constraint = constraint_part.split('-')[-1]

        fpath = os.path.sep.join((fdir, fname))
        schedule = naviio.xlsx2schedule(activity_book, fpath=fpath)

        print('\n\n\n\n============================================================')
        print('Iteration: {:4} / Constraint: {}'.format(iteration, constraint))
        navifunc.print_work_plan(schedule=schedule)
        time.sleep(1)