#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration


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

    Attribute
    ---------
    name : str
        | An activity name.
    productivity : int
        | The predetermined number of enable works of the activity.
    '''

    def __init__(self, name, productivity):
        self.name = name
        self.productivity = productivity