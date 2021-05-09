#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import pandas as pd


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

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z # floor information
        self.location_2d = tuple(self.x, self.y)
        self.location_3d = tuple(self.x, self.y, self.z)


class Activity:
    '''
    A class of an individual construction activity.

    Attributes
    ----------
    code : str
        | An unique code that represents the activity.
    name : str
        | An activity name.
    productivity : int
        | The predetermined number of enable works of the activity.
    '''

    def __init__(self, code, name, productivity):
        self.code = code
        self.name = name
        self.productivity = productivity

    def __str__(self):
        return self.name


class Work:
    '''
    A class to represent an activity on a grid.

    Attributes
    '''

    def __init__(self, grid, activity, day):
        self.grid = grid
        self.activity = activity
        self.day = day


class Project:
    '''
    A class to represent the whole construction project that consists of several works.
    '''

    def __init__(self, works):
        self.works = works
        self.grids = list(self.works.keys())

    def __iter__(self):
        for work in self.works:
            yield work

    def __call__(self):
        return self.works

    # def check_sequence_consistency(self):


## TODO: a kind of tree structure.
class ActivityTree:
    def __init__(self, sequences):
        self.sequences = sequences
        
    def order(self, activity1, activity2):
        return None # Return preceding activity