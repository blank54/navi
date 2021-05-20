#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
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
    prod : int
        | The predetermined number of enable works (i.e., productivity) of the activity.
    predecessor : list
        | A list of activities that should be done before the current activity.
    successor : list
        | A list of activities that should be done after the current activity.

    Methods
    -------
    add_predecessor
        | Add an activity on the "predecessor" list.
    add_successor
        | Add an activity on the "successor" list.
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

    def add_predecessor(self, activity):
        self.predecessor.append(activity)
        self.predecessor = list(set(self.predecessor))

    def add_successor(self, activity):
        self.successor.append(activity)
        self.successor = list(set(self.successor))


class ActivityTree:
    '''
    Attributes
    ----------
    leaves : list
        | A list of Activities.

    Methods
    -------
    check
        | Check the consistency between activity sequences.
    order
        | Return which activity should be done first.
    '''

    def __init__(self, leaves):
        self.leaves = leaves

    def __len__(self):
        return len(self.leaves)

    def check(self):
        return None
        
    def order(self, activity1, activity2):
        return None # activity1, activity2, or irrelevant


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