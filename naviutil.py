#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import time
import numpy as np
from copy import deepcopy
from collections import defaultdict


class NaviPath:
    root = os.path.dirname(os.path.abspath(__file__))
    
    fdir_template = os.path.sep.join((root, 'template'))
    fdir_component = os.path.sep.join((root, 'component'))
    fdir_data = os.path.sep.join((root, 'data'))
    fdir_proj = os.path.sep.join((root, 'proj'))
    fdir_schedule = os.path.sep.join((root, 'schedule'))

    activity_table = os.path.sep.join((fdir_template, 'activity_table.xlsx'))
    activity_order = os.path.sep.join((fdir_template, 'activity_order.xlsx'))
    activity_pre_dist = os.path.sep.join((fdir_template, 'activity_pre_dist.xlsx')) #choi 추가

    navisystem = os.path.sep.join((fdir_component, 'navisystem.pk'))

    def case(self, case_num):
        return os.path.sep.join((self.fdir_data, 'case_{}.xlsx'.format(case_num)))

    def proj(self, case_num):
        return os.path.sep.join((self.fdir_proj, 'proj_{}.pk'.format(case_num)))

    def schedule(self, case_num, note):
        return os.path.sep.join((self.fdir_schedule, 'schedule_N-{}_C-{}.xlsx'.format(case_num, note)))


class NaviFunc:
    def euclidean_distance(self, x, y):
        x_arr = np.array(x)
        y_arr = np.array(y)
        dist = np.linalg.norm(y_arr-x_arr)
        return dist

    def assign_activity_to_grid(self, schedule):
        work_plan = defaultdict(list)
        for location in schedule:
            for activity_code, day in schedule[location].items():
                work_plan[day].append((location, activity_code))

        xs, ys, zs = [], [], []
        for location in schedule:
            x, y, z = location.split('_')
            xs.append(int(x))
            ys.append(int(y))
            zs.append(int(z))

        layout_format = np.chararray((max(xs), max(ys)), itemsize=6, unicode=True)
        layout_format[:] = '------'

        work_layout = {}
        for day in work_plan:
            daily_layout = {z: deepcopy(layout_format) for z in set(zs)}
            for location, activity_code in work_plan[day]:
                x, y, z = location.split('_')
                col = int(x)-1
                row = int(y)-1
                flr = int(z)
                daily_layout[flr][row, col] = activity_code

            work_layout[day] = daily_layout
            del daily_layout

        return work_layout

    def print_schedule(self, schedule, timesleep=1):
        work_layout = self.assign_activity_to_grid(schedule)
        for day in sorted(work_layout.keys(), reverse=False):
            time.sleep(timesleep)
            print('\n\n\n\n============================================================')
            print('Work Layout: (Day: {})'.format(day))
            for flr in sorted(work_layout[day].keys(), reverse=False):
                print('--------------------------------------------------')
                print('Floor: {}'.format(flr))
                print(work_layout[day][flr])