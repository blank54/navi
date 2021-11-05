#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import time
import numpy as np
import pandas as pd
import pickle as pk
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


class NaviIO:
    def import_activity_book(self, **kwargs):
        fdir = kwargs.get('fdir', NaviPath().fdir_component)
        fname = kwargs.get('fname', 'activity_book.pk')
        fpath = kwargs.get('fpath', '')

        if not fpath:
            fpath = os.path.sep.join((fdir, fname))

        try:
            with open(fpath, 'rb') as f:
                activity_book = pk.load(f)
        except FileNotFoundError:
            print('Error: You should run "init.py" first to build "activity_book.pk"')

        return activity_book

    def schedule2xlsx(self, schedule, fname, verbose=True):
        '''
        Convert the schedule into a DataFrame format.
        '''

        schedule_dict = defaultdict(dict)
        for location in schedule:
            for day, activity_code in schedule[location].items():
                schedule_dict[day][location] = activity_code

        schedule_df = pd.DataFrame(schedule_dict)
        schedule_df = schedule_df.reindex(sorted(schedule_df.columns), axis=1)
        schedule_df = schedule_df.sort_index()

        os.makedirs(NaviPath().fdir_schedule, exist_ok=True)
        schedule_df.to_excel(os.path.sep.join((NaviPath().fdir_schedule, fname)), na_rep='', header=True, index=True)

        if verbose:
            print('Save Schedule')
            print('  | fdir : {}'.format(NaviPath().fdir_schedule))
            print('  | fname: {}'.format(fname))

    def xlsx2schedule(self, activity_book, **kwargs):
        fpath = kwargs.get('fpath', '')
        fname = kwargs.get('fname', '')

        if not fpath:
            fpath = os.path.sep.join((NaviPath().fdir_schedule, fname))

        schedule_df = pd.read_excel(fpath)
        schedule = defaultdict(dict)
        for row in schedule_df.iterrows():
            location = row[1]['Unnamed: 0']
            schedule[location] = {}
            for day, activity_code in row[1].items():
                if activity_code in activity_book.keys():
                    schedule[location][day] = activity_code

        return schedule
        

class NaviFunc:
    def order_bw_activity(self, activity_book, activity_code1, activity_code2):
        '''
        Attributes
        ----------
        activity_code1 : str
            | An activity code to compare the order.
        activity_code2 : str
            | Another activity code to compare the order.
        '''

        activity1 = activity_book[activity_code1]
        activity2 = activity_book[activity_code2]
        STATUS = None
        # consistency1 = self.check_order_consistency(activity1, activity2)
        if activity_code2 in activity1.predecessor:
            STATUS = 'TO_BE_MOVED'
        elif activity_code1 in activity2.predecessor:
            STATUS = 'PASS'
        else:
            STATUS = 'PASS'
        # consistency2 = self.check_order_consistency(activity2, activity1)


        # if all([(consistency1=='FINE'), (consistency2=='FINE')]):
        # if consistency1 == 'FINE':
        #     STATUS = 'PASS'
        # elif consistency1=='CONFLICT':
        #     STATUS = 'TO_BE_MOVED'
        # else:
        #     STATUS = 'IRRELEVANT'

        return STATUS

    def check_order(self, activity_book, show_irrelevant=False, show_conflict=True, show_error=True):
        '''
        Attributes
        ----------
        show_irrelevant : bool
            | To show irrelevant activity pairs. (default : False)
        show_conflict : bool
            | To show conflict activity pairs. (default : True)
        show_error : bool
            | To show errors in activity pairs. (default : True)
        '''

        fines = []
        irrelevants = []
        conflicts = []
        errors = []

        pairs = list(itertools.combinations(activity_book.keys(), 2))
        for activity_code1, activity_code2 in pairs:
            STATUS = self.order_bw_activity(activity_book, activity_code1, activity_code2)

            if STATUS == 'FINE':
                fines.append((activity_code1, activity_code2))
            elif STATUS == 'IRRELEVANT':
                irrelevants.append((activity_code1, activity_code2))
            elif STATUS == 'CONFLICT':
                conflicts.append((activity_code1, activity_code2))
            else:
                errors.append((activity_code1, activity_code2))

        print('Check orders (total: {:,} activities -> {:,} pairs)'.format(len(activity_book), len(pairs)))
        print('  | FINE:       {:,} pairs'.format(len(fines)))
        print('  | IRRELEVANT: {:,} pairs'.format(len(irrelevants)))
        print('  | CONFLICT:  {:,} pairs'.format(len(conflicts)))
        print('  | ERROR:     {:,} pairs'.format(len(errors)))

        if show_irrelevant and irrelevants:
            print('INFO: IRRELEVANT')
            for irrelevant in irrelevants:
                print('  | [{}] and [{}]'.format(irrelevant[0], irrelevant[1]))

        if show_conflict and conflicts:
            print('WARNING: CONFLICT')
            for conflict in conflicts:
                print('  | [{}] <-> [{}]'.format(conflict[0], conflict[1]))

        if show_error and errors:
            print('ERROR:')
            for error in errors:
                print('  | [{}] and [{}]'.format(error[0], error[1]))

        return fines, irrelevants, conflicts, errors

    # def check_order_consistency(self, activity_code1, activity_code2):
    #     '''
    #     Attributes
    #     ----------
    #     activity_code2 : str
    #         | An activity code of which order between the current activity is to be checked.
    #     '''
    #
    #     is_predecessor = False
    #     is_successor = False
    #
    #     if activity_code2 in activity_code1.predecessor:
    #         return 'CONFLICT'
    #         # is_predecessor = True
    #     else:
    #         return 'FINE'
            # pass
        # if activity_code2 in activity_code1.successor:
        #     is_successor = True
        # else:
        #     pass

        # if all((is_predecessor, is_successor)):
        # if is_predecessor == True :
        #     return 'FINE'
        # elif is_successor == True:
        #     return 'CONFLICT'
        # else:
        #     return 'ABSENT'

    def check_productivity_overload(self, activity_book, activity_code, count):
        try:
            if count > activity_book[activity_code].productivity:
                return 'overloaded'
            else:
                return 'fine'
        except KeyError:
            return 'fine'

    def grids2schedule(self, grids):
        '''
        Set an initial schedule of the project.
        '''

        schedule = defaultdict(dict)
        for grid in grids:
            schedule[grid.location] = {}

            day = 0
            while True:
                try:
                    schedule[grid.location][day] = grid.works[day].code
                    day += 1
                except IndexError:
                    break

        return schedule

    def sort_local_schedule(local_schedule):
        return sorted(local_schedule.items(), key=lambda x:x[1], reverse=False)

    def build_daily_work_plan(self, schedule):
        daily_work_plan = defaultdict(dict)
        for location in schedule:
            for day, activity_code in schedule[location].items():
                daily_work_plan[day][location] = activity_code

        return daily_work_plan

    def compare_schedule(self, schedule_1, schedule_2):
        if schedule_1.keys() != schedule_2.keys():
            return 'different'
        else:
            pass

        for location in schedule_1.keys():
            if len(schedule_1[location]) != len(schedule_2[location]):
                return 'different'
            else:
                pass

            for day, activity_code_1 in schedule_1[location].items():
                if activity_code_1 != schedule_2[location][day]:
                    return 'different'
                else:
                    continue

        return 'same'

    def compare_local_schedule(self, local_schedule_1, local_schedule_2):
        if len(local_schedule_1) != len(local_schedule_2):
            return 'different'
        else:
            pass

        for (day1, activity_code1), (day2, activity_code2) in zip(local_schedule_1.items(), local_schedule_2.items()):
            if activity_code1 == activity_code2:
                continue
            else:
                return 'different'

        return 'same'

    def euclidean_distance(self, x, y):
        x_arr = np.array(x, dtype='i1')
        y_arr = np.array(y, dtype='i1')
        dist = np.linalg.norm(y_arr-x_arr)
        return dist

    def assign_activity_to_grid(self, schedule):
        work_plan = defaultdict(list)
        for location in schedule:
            for day, activity_code in schedule[location].items():
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

    def print_work_layout(self, schedule, timesleep=1):
        work_layout = self.assign_activity_to_grid(schedule)
        for day in sorted(work_layout.keys(), reverse=False):
            time.sleep(timesleep)
            print('\n\n\n\n============================================================')
            print('Work Layout: (Day: {})'.format(day))
            for flr in sorted(work_layout[day].keys(), reverse=False):
                print('--------------------------------------------------')
                print(work_layout[day][flr])

    def print_work_plan(self, schedule):
        location_list = sorted(schedule.keys())
        daily_work_plan = self.build_daily_work_plan(schedule=schedule)

        print('--------------------------------------------------')
        print('  | day   '+'  '.join(location_list)+'\n')

        for day in sorted(daily_work_plan.keys()):
            daily_works = []
            for location in location_list:
                try:
                    activity_code = daily_work_plan[day][location]
                except KeyError:
                    activity_code = '------'

                daily_works.append(activity_code)

            print('  |  {:3} '.format(day)+' '.join(daily_works))
