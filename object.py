#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
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
    activities : dict
        | A dictionary of activities of which keys are activity_code and values are activity (i.e., the class of Activity).
    grids : list
        | A list of grids (i.e., the class of Grid).
    duration : int
        | The duration of the project that determined by the user.
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

        self.bag_of_activity_code = []
        self.schedule = []
        self.sorted_grids = ''

        self.__initialize()
        self.__sort_grids()

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

    ## TODO: Sort the grids by starting at a grid with the longest workdays and move to the nearest grid.
    def __sort_grids(self):
        self.sorted_grids = self.grids

    def __get_local_works(self, location):
        works = [work for work in self.schedule if work.grid.location == location]
        sorted_works = sorted(works, key=lambda x:x.day, reverse=False)
        return sorted_works

    def __check_productivity(self, activity_stack, next_activity):
        '''
        If the number of activities existing in the stack is smaller than the activity's productivity, return True.
        '''

        if activity_stack[next_activity.code] < self.activities[next_activity.code].productivity:
            return True
        else:
            return False

    def __check_pre_dist(self):
        return True

    def reschedule(self):
        updated_schedule = []

        local_works = {}
        for grid in self.grids:
            local_works[grid.location] = self.__get_local_works(location=grid.location)

        day = 0
        ## TODO: Return warning if the day becomes larger than the duration.
        while day <= self.duration:

            ## Initialize activity stack.
            activity_stack = {activity_code: 0 for activity_code in self.activities.keys()}

            ## Try to assign a work on each grid.
            ## TODO: Start at a grid with the longest workdays and move to the nearest grid.
            for grid in self.sorted_grids:
                remaining_works = local_works[grid.location]
                if not remaining_works:
                    continue

                ## Get the first remaining work on the grid.
                next_work = remaining_works[0]
                next_activity = next_work.activity
                
                ## If productivity on the day is full, remain the grid blank and move to the next.
                if not self.__check_productivity(activity_stack=activity_stack, next_activity=next_activity):
                    continue

                ## TODO: If predecessors around not over yet, remain the grid blank and move to the next.
                if not self.__check_pre_dist():
                    continue



                # 해당 day에 bbb작업이 배정되려면 선행작업의 완료 영역을 확인한다.
                # bbb작업의 선행작업이 무엇인가
                # bbb작업은 어디에 진행중인가
                # 선행완료 영역의 거리는 어느 그리드를 포함하는가
                # 해당 그리드에 선행작업이 있는가?
                # 작업을 배정한다
                #

                ## >>WORK HERE<<
                '''
                Develop your code here.
                Then, run 'test/reschedule.py' to test the code.
                You can find the result directories on 'naviutil.py'
                '''




                ## If all of the constraints are okay, assign the work.
                # else:
                next_work = remaining_works.pop(0)
                work = Work(grid=grid, day=day, activity=next_work.activity)
                updated_schedule.append(work)
                activity_stack[work.activity.code] += 1

            ## Once every grid passed the work assignment process, move to the next day.
            day += 1

        ## TODO: Assign same works to close grids.

        ## TODO: Check activity orders.

        ## TODO: Push some duration-free works to be conducted in the same day.

        ## TODO: Return error if any work remains in local_works.

        ## Update the schedule and sort the grids again.
        self.schedule = updated_schedule
        self.__sort_grids()

    def summary(self):
        '''
        Summarize the project schedule.
        '''

        print('Project Summary')
        print('  | Duration: {} days'.format(self.duration))
        
    def export(self, fpath):
        '''
        Export the project schedule in the format of ".xlsx".

        Attributes
        ----------
        fpath : str
            | FilePath for the exported schedule.
        '''

        schedule_dict = defaultdict(dict)
        for day in range(self.duration):
            schedule_dict[day] = {}

        for work in self.schedule:
            schedule_dict[work.day][work.grid.location] = work.activity.code

        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        schedule_df = pd.DataFrame(schedule_dict)
        schedule_df.to_excel(fpath, na_rep='', header=True, index=True)