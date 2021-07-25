#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import sys
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from naviutil import NaviFunc
navifunc = NaviFunc()

import random
import itertools
import pandas as pd
from copy import deepcopy
from collections import defaultdict


class Activity:
    '''
    A class of an individual construction activity.

    Attributes
    ----------
    code : str
        | An unique code that represents the activity.
    category : str
        | Category name of the activity.
    major : str
        | Major activity name. (i.e., work package)
    minor : str
        | Minor activity name.
    productivity : int
        | The predetermined number of enable works (i.e., productivity) of the activity.
    predecessor : list
        | A list of activity codes that should be done before the current activity.
    successor : list
        | A list of activity codes that should be done after the current activity.

    Methods
    -------
    add_predecessor
        | Add an activity code on the "predecessor" list.
    add_successor
        | Add an activity code on the "successor" list.
    check_order_consistency
        | Check order consistency between current activity and the input activity code.
    '''

    def __init__(self, parameters):
        self.code = parameters.get('code', 'NA')

        self.category = parameters.get('category', 'NA')
        self.major = parameters.get('major', 'NA')
        self.minor = parameters.get('minor', 'NA')
        
        self.productivity = parameters.get('productivity', 'NA')

        self.predecessor = []
        self.successor = []

    def __str__(self):
        return '{}: {}'.format(self.code, self.minor)

    def add_predecessor(self, activity_code):
        '''
        Attributes
        ----------
        activity_code : str
            | A code of predecessor activity.
        '''

        self.predecessor.append(activity_code)
        self.predecessor = list(set(self.predecessor))

    def add_successor(self, activity_code):
        '''
        Attributes
        ----------
        activity_code : str
            | A code of successor activity.
        '''

        self.successor.append(activity_code)
        self.successor = list(set(self.successor))

    def check_order_consistency(self, activity_code):
        '''
        Attributes
        ----------
        activity_code : str
            | An activity code of which order between the current activity is to be checked.
        '''

        is_predecessor = False
        is_successor = False

        if activity_code in self.predecessor:
            is_predecessor = True
        else:
            pass
        if activity_code in self.successor:
            is_successor = True
        else:
            pass

        if all((is_predecessor, is_successor)):
            return 'CONFLICT'
        elif any((is_predecessor, is_successor)):
            return 'FINE'
        else:
            return 'ABSENT'


class NaviSystem:
    '''
    A construction procedure navigation system.

    Attributes
    ----------
    activities : dict
        | A dict of Activities of which keys are activity code.

    Methods
    -------
    order_bw_activity
        | Return which activity should be done first.
    check_order
        | Check the order consistency between activities.
    '''

    def __init__(self, activities):
        self.activities = activities

    def __len__(self):
        return len(self.activities)
        
    def order_bw_activity(self, activity_code1, activity_code2):
        '''
        Attributes
        ----------
        activity_code1 : str
            | An activity code to compare the order.
        activity_code2 : str
            | Another activity code to compare the order.
        '''

        activity1 = self.activities[activity_code1]
        activity2 = self.activities[activity_code2]

        consistency1 = activity1.check_order_consistency(activity2.code)
        consistency2 = activity2.check_order_consistency(activity1.code)
        STATUS = None

        if all([(consistency1=='FINE'), (consistency2=='FINE')]):
            STATUS = 'FINE'
        elif any([(consistency1=='CONFLICT'), (consistency2=='CONFLICT')]):
            STATUS = 'CONFLICT'
        else:
            STATUS = 'IRRELEVANT'

        return STATUS

    def check_order(self, show_irrelevant=False, show_conflict=True, show_error=True):
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

        pairs = list(itertools.combinations(self.activities.keys(), 2))
        for activity_code1, activity_code2 in pairs:
            STATUS = self.order_bw_activity(activity_code1, activity_code2)

            if STATUS == 'FINE':
                fines.append((activity_code1, activity_code2))
            elif STATUS == 'IRRELEVANT':
                irrelevants.append((activity_code1, activity_code2))
            elif STATUS == 'CONFLICT':
                conflicts.append((activity_code1, activity_code2))
            else:
                errors.append((activity_code1, activity_code2))

        print('Check orders (total: {:,} activities -> {:,} pairs)'.format(self.__len__(), len(pairs)))
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

    # def __sort_activities(self):
    #     ## Check activity order consistency.
    #     _, _, conflicts, errors = self.check_order()

    #     if any((conflicts, errors)):
    #         print('>>>Debug activity orders')
    #         return None
    #     else:
    #         pass

    #     sorted_activity_list = list(set(self.activities.keys()))
    #     while :
    #         random.shuffle(sorted_activity_list)
    #         for idx in range(len(sorted_activity_list)-1):
    #             left_code = sorted_activity_list[idx]
    #             left_activity = self.activities[left_code]

    #             right_code = sorted_activity_list[idx+1]
    #             right_activity = self.activities[right_code]

    #     return sorted_activity_list


class Work:
    '''
    A class to represent an activity on a grid.

    Attributes
    ----------
    grid : Grid
        | The grid of the work.
    day : int
        | The day of the work.
    activity : Activity
        | The Activity class.
    '''

    def __init__(self, grid, day, activity):
        self.grid = grid
        self.day = day
        self.activity = activity


class Grid:
    '''
    A class that represents a single location.

    Attributes
    ----------
    x : int
        | Horizontal location of the location.
    y : int
        | Vertical location of the location.
    z : int
        | Depth of the location.
    location_2d : tuple
        | 2-dimensional location of a grid.
    location_3d : tuple
        | 3-dimensional location of a grid.
    '''

    def __init__(self, location, works):
        self.location = location

        self.x, self.y, self.z = [int(l) for l in self.location.split('_')]
        self.location_2d = tuple((self.x, self.y))
        self.location_3d = tuple((self.x, self.y, self.z))

        self.works = works

    def __len__(self):
        return len(self.works)


class Project:
    '''
    A class to represent the whole construction project that consists of several works.

    Attributes
    ----------
    activities : dict
        | A dictionary of activities of which keys are activity_code and values are activity (i.e., the class of Activity).
    grids : list
        | A list of grids (i.e., the class of Grid).
    duration : int
        | The duration of the project that determined by the user.
    duration_expected : int
        | The expected duration of the project based on the current schedule.
    bag_of_activity_code : list
        | A list of activity codes that have been used in the project.
    schedule : list
        | A list of works (i.e., the class of Work).
    sorted_grids : list
        | A list of grids that are sorted based on the distance from the grid with the longest workday.

    Methods
    -------
    search
        | To find location and workday for an activity.
    '''

    def __init__(self, activities, grids, duration):
        self.activities = activities
        self.grids = grids
        self.duration = duration
        self.duration_expected = ''

        self.bag_of_activity_code = list(set(itertools.chain(*[[activity.code for activity in grid.works] for grid in self.grids])))
        self.schedule = {}
        self.sorted_grids = []

        self.__initialize()
        self.__sort_grids()
        self.__estimate_duration()

    def __len__(self):
        '''
        Total number of activities to be conducted for the project.
        '''

        return len(list(itertools.chain(*[[activity for activity in grid.works] for grid in self.grids])))

    def __initialize(self):
        '''
        Set an initial schedule of the project.
        '''

        for grid in self.grids:
            self.schedule[grid.location] = {}

            day = 0
            while True:
                try:
                    self.schedule[grid.location][grid.works[day].code] = day
                    day += 1
                except IndexError:
                    break

    def __sort_grids(self):
        '''
        Sort the grids by starting at a grid with the longest workdays and move to the nearest grid.
        '''

        sorted_by_work_len = sorted(self.grids, key=lambda x:len(x.works), reverse=True)
        worklen2grid = defaultdict(list)
        for grid in sorted_by_work_len:
            worklen2grid[len(grid.works)].append(grid)

        sorted_by_dist = []
        for worklen, grids_same_worklen in sorted(worklen2grid.items(), key=lambda x:x[0], reverse=True):
            while len(grids_same_worklen) > 0:
                try:
                    last_grid = sorted_by_dist[-1]
                except IndexError:
                    last_grid = grids_same_worklen[0]

                grids_same_worklen = sorted(grids_same_worklen, key=lambda x:navifunc.euclidean_distance(x.location_3d, last_grid.location_3d), reverse=False)
                sorted_by_dist.append(grids_same_worklen[0])
                grids_same_worklen.pop(0)

        self.sorted_grids = sorted_by_dist

    def __estimate_duration(self):
        '''
        Estimate the project duration based on the current schedule.
        '''

        duration_expected = 0
        for location in self.schedule:
            last_day = max(list(self.schedule[location].values()))
            if duration_expected <= last_day:
                duration_expected = deepcopy(last_day)

        self.duration_expected = duration_expected

    def summary(self, duration=False, sorted_grids=False):
        '''
        Summarize the project schedule.
        '''

        print('============================================================')
        print('Project Summary')

        if duration:
            self.__estimate_duration()
            print('============================================================')
            print('Duration')
            print('  | Planned : {:,} days'.format(self.duration))
            print('  | Expected: {:,} days'.format(self.duration_expected))

        if sorted_grids:
            self.__sort_grids()
            print('============================================================')
            print('Sorted Grids')
            for grid in self.sorted_grids:
                print('  | Location: ({:>2} {:>2} {:>2}) -> WorkLen: {:>3,}'.format(grid.x, grid.y, grid.z, len(grid.works)))

    def schedule2df(self):
        '''
        Convert the schedule into a DataFrame format.
        '''

        schedule_dict = defaultdict(dict)
        for location in self.schedule:
            for activity_code, day in self.schedule[location].items():
                schedule_dict[day][location] = activity_code

        schedule_df = pd.DataFrame(schedule_dict)
        return schedule_df.reindex(sorted(schedule_df.columns), axis=1)

    def export(self, fpath):
        '''
        Export the project schedule in the format of ".xlsx".

        Attributes
        ----------
        fpath : str
            | FilePath for the exported schedule.
        '''

        schedule_df = self.schedule2df()
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        schedule_df.to_excel(fpath, na_rep='', header=True, index=True)

    def search(self, activity_code, verbose=False):
        '''
        A method to find location and workday for an activity.
        Input the code of the activity.

        Attributes
        ----------
        activity_code : str
            | The predetermined code of the activity that the user wants to search.
        '''

        here = []
        for location in self.schedule:
            if activity_code in self.schedule[location].keys():
                day = self.schedule[location][activity_code]
                here.append((location, day))

        if verbose:
            print('Find {}:'.format(activity_code))
            print('  | LOCATION | DAY |')
            for location, day in sorted(here, key=lambda x:x[1], reverse=False):
                print('  | {:<7} | {:>3} |'.format(location, day))
        else:
            pass

        return here