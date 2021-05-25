#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
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


class ActivityTree:
    '''
    A class of activity structure that includes various checking tools of constraints.

    Attributes
    ----------
    leaves : dict
        | A dict of Activities of which keys are activity code.

    Methods
    -------
    __order_bw_activity
        | Return which activity should be done first.
    check_order
        | Check the order consistency between activities.
    '''

    def __init__(self, leaves):
        self.leaves = leaves

    def __len__(self):
        return len(self.leaves)
        
    def __order_bw_activity(self, activity_code1, activity_code2):
        '''
        Attributes
        ----------
        activity_code1 : str
            | An activity code to compare the order.
        activity_code2 : str
            | Another activity code to compare the order.
        '''

        activity1 = self.leaves[activity_code1]
        activity2 = self.leaves[activity_code2]

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

        pairs = list(combinations(self.leaves.keys(), 2))
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


class Work:
    '''
    A class to represent an activity on a grid.

    Attributes
    ----------
    activity : Activity
        | The Activity class.
    day : int
        | The work day from the beginning.
    '''

    def __init__(self, activity, day):
        self.activity = activity
        self.day = day


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
    works : list
        | A list of Work that is conducted on the grid.
    last_day : int
        | The last working day of works.
    duration : int
        | Total working day on the grid.
    '''

    def __init__(self, location):
        self.x, self.y, self.z = [int(l) for l in location.split('_')]
        self.location_2d = tuple((self.x, self.y))
        self.location_3d = tuple((self.x, self.y, self.z))

        self.works = []

        self.last_day = ''
        self.duration = ''

    def __len__(self):
        return len(self.works)

    def __iter__(self):
        for work in self.works:
            yield work

    def update(self):
        self.last_day = max([w.day for w in self.works], default=0)
        self.duration = self.last_day+1 # The working day starts with 0

    ## TODO
    # def delay_from_here(self, day)


class Project:
    '''
    A class to represent the whole construction project that consists of several works.

    Attributes
    ----------
    grids : list
        | A list of grids.
    critical_grids : list
        | The grids whose workday is the longest.

    Methods
    -------
    find_critical_grids
        | To find the longest work.
    adjust_all
        | Adjust every work based on the critical grid.
    adjust_one
        | Adjust one work based on the critical grid.
    '''

    def __init__(self, grids):
        self.grids = grids

        self.duration = None
        self.critical_grids = None
        self.schedule = None

        self.update()

    def __iter__(self):
        for location in self.grids:
            yield self.grids[location]

    def __update_duration(self):
        self.duration = max([grid.duration for loc, grid in self.grids.items()])

    def __update_critical_grids(self):
        self.critical_grids = [loc for loc, grid in self.grids.items() if grid.duration == self.duration]

    def __update_schedule(self):
        schedule = defaultdict(list)
        for day in range(self.duration):
            for loc, grid in self.grids.items():
                try:
                    work_today = [w for w in grid if w.day == day][0]
                    schedule[day].append('{:>10}'.format(work_today.activity.code))
                except IndexError:
                    schedule[day].append('{:>10}'.format(''))
        self.schedule = pd.DataFrame(schedule, index=list(self.grids.keys()))

    def update(self):
        self.__update_duration()
        self.__update_critical_grids()
        self.__update_schedule()

    ## TODO
    def adjust_one(self, location):
        for w2 in self.grids[location]:
            for critical_grid in self.critical_grids:
                for w1 in self.grids[location]:

                    # Same activity with critical grid --> work in the same day
                    if w1.activity.code == w2.activity.code:
                        if w2.day < w1.day:
                            w2.day = deepcopy(w1.day)

    def adjust_all(self):
        for loc in self.grids:
            self.adjust_one(location=loc)

    def summary(self):
        print('____________________________________________________________')
        print('Duration: {} days'.format(self.duration))
        print('Critical Grids: {}'.format(self.critical_grids))
        print()
        print('Schedule:')
        print(self.schedule)
        print('____________________________________________________________')

    def export(self, fpath):
        self.schedule.to_excel(fpath, na_rep='', header=True, index=True)