#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
from copy import deepcopy


# class Grid:
#     '''
#     A class that represents a single grid.

#     Attributes
#     ----------
#     x : int
#         | horizontal location of the grid.
#     y : int
#         | vertical location of the grid.
#     z : int
#         | depth of the grid.
#     '''

#     def __init__(self, x, y, z):
#         self.x = x
#         self.y = y
#         self.z = z # floor information
#         self.location_2d = tuple(self.x, self.y)
#         self.location_3d = tuple(self.x, self.y, self.z)


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


## TODO: a kind of tree structure.
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

    def __init__(self, grid, activity, day):
        self.grid = grid
        self.activity = activity
        self.day = day


class Project:
    '''
    A class to represent the whole construction project that consists of several works.

    Attributes
    ----------
    works : list
        | A list of works.
    grids : list
        | A list of grid names.
        | TODO: The Grid class will be used in the future.
    critical_grid : str
        | The grid whose workday is the longest.

    Methods
    -------
    find_critical_grid
        | To find the longest work.
    adjust_all
        | Adjust every work based on the critical grid.
    adjust_one
        | Adjust one work based on the critical grid.
    '''

    def __init__(self, works):
        self.works = works
        self.grids = list(self.works.keys())

        self.critical_grid = ''

    def __iter__(self):
        for work in self.works:
            yield work

    def __call__(self):
        return self.works

    def find_critical_grid(self):
        self.critical_grid = 'A1'

    ## TODO
    def adjust_all(self):
        if not self.critical_grid:
            print('ERROR: No critical grid exists. Please run ".find_critical_grid" first.')
            return None

        return None

    def adjust_one(self, grid):
        if not self.critical_grid:
            print('ERROR: No critical grid exists. Please run ".find_critical_grid" first.')
            return None

        for w2 in self.works[grid]:
            for w1 in self.works[self.critical_grid]:
                if w1.activity.name == w2.activity.name:
                    if w2.day < w1.day:
                        w2.day = deepcopy(w1.day)