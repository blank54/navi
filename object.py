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
    name : str
        | An activity name.
    prod : int
        | The predetermined number of enable works (i.e., productivity) of the activity.
    previous : list
        | A list of activities that should be done before the current activity.
    next : list
        | A list of activities that should be done after the current activity.

    Methods
    -------
    add_previous
        | Add an activity on the "previous" list.
    add_next
        | Add an activity on the "next" list.
    '''

    def __init__(self, name, code, prod):
        self.name = name
        self.code = code
        self.prod = prod

        self.previous = []
        self.next = []

    def __str__(self):
        return self.name

    def add_previous(self, activity):
        self.previous.append(activity)
        self.previous = list(set(self.previous))

    def add_next(self, activity):
        self.next.append(activity)
        self.next = list(set(self.next))


class ActivityTree:
    '''
    Methods
    -------
    check
        | Check the consistency between activity sequences.
    order
        | Return which activity should be done first.
    '''

    def __init__(self, leaves):
        self.leaves = leaves

    def check(self):
        return None
        
    def order(self, activity1, activity2):
        return None # activity1, activity2, or irrelevant


class Work:
    '''
    A class to represent an activity on a grid.

    Attributes
    ----------
    grid : str
        | A grid name (e.g., "A1", "A2", ...)
        | TODO: The Grid class will be used in the future.
    activity : Activity
        | The Activity class.
    day : int
        | The work day from the beginning.
    '''

    def __init__(self, location, activity, day):
        self.location = location
        self.activity = activity
        self.day = day


class Grid:
    '''
    A class that represents a single grid.

    Attributes
    ----------
    x : int
        | horizontal location of the grid.
    y : int
        | vertical location of the grid.
    z : int
        | depth of the grid.
    '''

    # def __init__(self, x, y, z):
    #     self.x = x
    #     self.y = y
    #     self.z = z # floor information
    #     self.location_2d = tuple(self.x, self.y)
    #     self.location_3d = tuple(self.x, self.y, self.z)

    def __init__(self, location, works):
        self.location = location
        self.works = works

        self.duration = max([w.day for w in self.works])+1 # The working day starts with 0

    def __len__(self):
        return len(self.works)

    def __iter__(self):
        for work in self.works:
            yield work

    ## TODO
    # def delay_from_here(self, day)


class Project:
    '''
    A class to represent the whole construction project that consists of several works.

    Attributes
    ----------
    works : dict
        | A dict of works whose key is a grid.
    grids : list
        | A list of grid names.
        | TODO: The Grid class will be used in the future.
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
        self.grid_list = list(self.grids.keys())

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
                    schedule[day].append('{:>5}'.format(work_today.activity.name))
                except IndexError:
                    schedule[day].append('{:>5}'.format(''))
        self.schedule = pd.DataFrame(schedule, index=self.grid_list)

    def update(self):
        self.__update_duration()
        self.__update_critical_grids()
        self.__update_schedule()

    def adjust_one(self, location):
        for w2 in self.grids[location]:
            for critical_grid in self.critical_grids:
                for w1 in self.grids[location]:

                    # Same activity with critical grid --> work in the same day
                    if w1.activity.name == w2.activity.name:
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