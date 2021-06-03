#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import random
import pandas as pd
from copy import deepcopy
from itertools import combinations
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
    prod : int
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
        
        self.prod = parameters.get('productivity', 'NA')

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
    __order_bw_activity
        | Return which activity should be done first.
    check_order
        | Check the order consistency between activities.
    '''

    def __init__(self, activities):
        self.activities = activities

    def __len__(self):
        return len(self.activities)
        
    def __order_bw_activity(self, activity_code1, activity_code2):
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

        pairs = list(combinations(self.activities.keys(), 2))
        for activity_code1, activity_code2 in pairs:
            STATUS = self.__order_bw_activity(activity_code1, activity_code2)

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
    grids : list
        | A list of grids.

    Methods
    -------
    adjust_all
        | Adjust every work based on the critical grid.
    adjust_one
        | Adjust one work based on the critical grid.
    '''

    def __init__(self, activities, grids, duration):
        self.activities = activities
        self.grids = grids
        self.duration = duration

        self.bag_of_activity_code = []
        self.schedule = []

        self.__initialize()

    def __len__(self):
        return max([work.day for work in self.schedule])+1

    def __initialize(self):
        bag_of_activity_code = []

        for grid in self.grids:
            bag_of_activity_code.extend([activity.code for activity in grid.works])

            for day in range(self.duration):
                try:
                    self.schedule.append(Work(grid=grid, day=day, activity=grid.works[day]))
                except IndexError:
                    continue

        self.bag_of_activity_code = list(set(bag_of_activity_code))

    def find(self, activity_code, verbose=False):
        here = []
        for work in self.schedule:
            if activity_code == work.activity.code:
                here.append(work)

        if verbose:
            print('Fine {}:'.format(activity_code))
            print('  | LOCATIN | DAY |')
            for work in sorted(here, key=lambda x:x.day, reverse=False):
                print('  | {:<7} | {:>3} |'.format(work.grid.location, work.day))
        else:
            pass

        return here

    def push_workday(self, location, start_day, change):
        for work in self.schedule:
            if work.grid.location == location:
                if work.day >= start_day:
                    work.day += change
                else:
                    continue
            else:
                continue

    def __find_earliest_workday(self, activity_code):
        workdays = []
        for grid in self.grids:
            workdays.extend([idx for idx, activity in enumerate(grid.works) if activity.code == activity_code])

        return min(workdays)

    def __sort_activities(self, activity_list):
        ranks = defaultdict(int)
        for code_i, code_j in combinations(activity_list, r=2):
            activity_i = self.activities[code_i]
            activity_j = self.activities[code_j]

            if activity_j in activity_i.predecessor:
                ranks[code_i] += 1
            elif activity_j in activity_i.successor:
                ranks[code_j] += 1
            else:
                ranks[code_i] += 0
                ranks[code_j] += 0

        return [code for code in sorted(ranks.keys(), key=lambda x:x[1], reverse=False)]

    def __connect_pivot_works(self, earliest_days):
        pivot_works = []
        for day in sorted(earliest_days.keys()):
            if len(earliest_days[day]) == 1:
                activity_code = earliest_days[day][0]
                pivot_works.append(activity_code)
            else:
                ## TODO: Compare activity orders
                pivot_works.extend(self.__sort_activities(activity_list=earliest_days[day]))

        return pivot_works

    def reschedule_one-day_one-activity(self):
        updated_schedule = []

        ## Find the earliest workday for each activity.
        earliest_days = defaultdict(list)
        for activity_code in self.bag_of_activity_code:
            day = self.__find_earliest_workday(activity_code=activity_code)
            earliest_days[day].append(activity_code)

        ## Connect activities.
        pivot_works = self.__connect_pivot_works(earliest_days=earliest_days)

        ## Assign workday
        when_to_do = {activity_code: day for day, activity_code in enumerate(pivot_works)}
        for grid in self.grids:
            for activity in grid.works:
                day = when_to_do[activity.code]
                updated_schedule.append(Work(grid=grid, day=day, activity=activity))
            
        self.schedule = updated_schedule

    ## TODO: Push workdays based on productivity
    def reschedule_push_and_pull(self):
        # for day in range(self.__len__()):
        #     for work in [work for work in self.schedule if work.day == day]:
        #         print(work.activity.prod)
        pass

    def summary(self):
        print('____________________________________________________________')
        print('Duration: {} days'.format(self.duration))
        print()
        print('Schedule:')
        print(self.schedule)
        print('____________________________________________________________')

    def export(self, fpath):
        schedule_dict = defaultdict(dict)
        for day in range(self.duration):
            schedule_dict[day] = {}

        for work in self.schedule:
            schedule_dict[work.day][work.grid.location] = work.activity.code

        schedule_df = pd.DataFrame(schedule_dict)
        schedule_df.to_excel(fpath, na_rep='', header=True, index=True)