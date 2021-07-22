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
import pandas as pd
from copy import deepcopy
import itertools
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

        pairs = list(combinations(self.activities.keys(), 2))
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
        self.schedule = []
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
            day = 0
            while True:
                try:
                    self.schedule.append(Work(grid=grid, day=day, activity=grid.works[day]))
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

        self.duration_expected = max([work.day for work in self.schedule])+1

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
        num_of_assigned_activity = 0
        while True:
            print(day)
            ## Initialize activity stack.
            activity_stack = {activity_code: 0 for activity_code in self.activities.keys()}

            ## Try to assign a work on each grid.
            for grid in self.sorted_grids:
                remaining_works = local_works[grid.location]
                if not remaining_works:
                    continue

                ## Get the first remaining work on the grid.
                next_activity = remaining_works[0].activity

                if next_activity.code == 'M00009':
                    next_work = remaining_works.pop(0)
                    work = Work(grid=grid, day=1000, activity=next_work.activity)
                    updated_schedule.append(work)
                    activity_stack[work.activity.code] += 1
                    num_of_assigned_activity += 1
                    continue
                
                ## If productivity on the day is full, remain the grid blank and move to the next.
                if not self.__check_productivity(activity_stack=activity_stack, next_activity=next_activity):
                    continue

                ## TODO: If predecessors around not over yet, remain the grid blank and move to the next.
                if not self.__check_pre_dist():
                    continue


#########
#7월22일 수도코드

                #생산성 제약
                # day에 grid에 activity 배정
                # activity의 productivity 확인
                # productivity >= day에 배정된 activity 개수
                # True : next grid
                # False : next day

#여기까지는 위에 코딩 된거죠?


                # 선행완료 거리 제약
                # day에 grid에 activity의 선행완료 거리값
                # z=z and 선행완료 거리값 **2 >= (x-x)**2, (y-y)**2 인 grid_dist_range
                # grid에 배정된 activity와 grid_dist_range 내 activity 선후관계
                # if grid_dist_range 내 activity가 grid에 배정된 activity보다 선행작업이 있으면 :
                # grid에 배정된 activity day+1 배정
                # else :  day에 배정

                # 생산성 제약 재검토_1
                # day에 activity개수와 activity의 productivity 확인
                # productivity >= day에 배정된 activity 개수
                # True : next day
                # False :
                # day에 activity가 있는 그리드, count(remaining activity),
                # 개수가 가장 적은 grid
                # activity day+1에 배정

                # 선행완료 거리 제약 재검토_1
                # day에 grid에 activity의 선행완료 거리값
                # z=z and 선행완료 거리값 **2 >= (x-x)**2, (y-y)**2 인 grid_dist_range
                # grid에 배정된 activity와 grid_dist_range 내 activity 선후관계
                # if grid_dist_range 내 activity가 grid에 배정된 activity보다 선행작업이 있으면 :
                # grid에 배정된 activity 다음날 배정
                # else :  day에 배정

                # 생산성 제약 재검토_2
                # day에 activity개수와 activity의 productivity 확인
                # productivity >= day에 배정된 activity 개수
                # True : next day
                # False :
                # day에 activity가 있는 그리드, count(remaining activity),
                # 개수가 가장 적은 grid
                # activity day+1에 배정

                # 선행완료 거리 제약 재검토_2
                # day에 grid에 activity의 선행완료 거리값
                # z=z and 선행완료 거리값 **2 >= (x-x)**2, (y-y)**2 인 grid_dist_range
                # grid에 배정된 activity와 grid_dist_range 내 activity 선후관계
                # if grid_dist_range 내 activity가 grid에 배정된 activity보다 선행작업이 있으면 :
                # grid에 배정된 activity 다음날 배정
                # else :  day에 배정


                # 단면 선후조건 제약
                # if activity code가 D or R로 시작하는 activity :
                    # if activity == activity and x==x and y==y and z!=z:
                        #z가 큰 그리드가 선행
                    # else: next
                #else : next
                #D or R로 시작하는 작업의 그리드 순서 리스트 작성

                # 단면 선후조건 제약
                # if activity code가 S or R로 시작하는 activity :
                    # if activity == activity and x==x and y==y and z!=z:
                        # z가 작은 그리드가 선행
                # else: next
                # else : next
                # D or R로 시작하는 작업의 그리드 순서 리스트 작성

                # 단면 선행완료 제약 적용
                # day에 grid(x, y, -1)에 D00000작업은
                # grid_dist_range = z=1 and 선행완료 거리값 **2 >= (x-x)**2, (y-y)**2인 grid list
                # if grid_dist_range 내 activity가 grid에 배정된 activity보다 선행작업이 있으면 :
                    # grid에 배정된 activity day+1 배정
                # else :  day에 배정

                # day에 grid(x, y, -2)에 D00000작업은
                # grid_dist_range = z=-1 and 선행완료 거리값 **2 >= (x-x)**2, (y-y)**2인 grid list
                # if grid_dist_range 내 activity가 grid에 배정된 activity보다 선행작업이 있으면 :
                    # grid에 배정된 activity day+1 배정
                # else :  day에 배정
##############
#7월 22일 나름대로 수도코드

                    # x==x and y==y and z!=z 인 activity는 z값이 큰 것이 day에 배정


                # 터파기, 스트러트 작업은 동일한 x,y에서 Z축의 값이 1, -1, -2,...으로 진행되어야 함. (지하공사는 위에서 아래로 진행하기 때문)
                # 지하 1층에 터파기 작업이 일정 영역이상 진행되어야 지하2층 터파기 작업이 가능(선행완료영역 제약)

                # 터파기 시  흙막이 주변 소단형성, 스트러트, 어스앵커 등 흙막이 지지 작업 완료 후 소단 터파기 진행가능
                # 예) 1층 터파기작업 9개 그리드 완료(1,1,1 ~ 3,3,1), 그리드 (1,1,1), (2,1,1), (3,1,1), (1,2,1),.(1,3,1) 소단 형성
                # 흙막이 지지 작업 완료 후 소단 제거(1,1,1)
                # 터파기 작업 거리 2인 경우 (2,2,-1) 터파기 진행 가능, 그외 작업 진행 불가


                # 기존 공정표에 작업으로 표현하지 않고 전문업체의 경험과 관리자의 경험으로 수행하는 작업들을 정의 필요.
                # 단점일 수 있으나,BIM 모델링을 하지 않는 객체에 대해 데이터를 넣을 수 있는 그릇이 될 수 있음.



                # 골조공사는 동일한 x, y에서 z축의 값이 -n, -n+1, ...-2,-1,1 순으로 진행되어야 함.. (골조공사는 아래에서 위로 진행하기 때문)


                # 지하슬래브를 터파기순서대로 진행하는 지하역타 공법 적용방법, ID D or R적용
                # if Activity ID첫 문자가 D or R인 경우, z축 값 순서 -1씩 더하여 진행


                # 지하수직재와 지상 골조를 별도로 시공하는 탑다운 공법 적용방법
                # 1층 수직재의 시작점을 제시하는 마일스톤 작업 배정하여 마일스톤 작업 이후 지상골조는 골조공사 기준에 따라 진행하도록 함
                # 골조공사는 동일한 x, y에서 z축의 값이 -n, -n+1, ...-2,-1,1 순으로 진행되어야 함.. (골조공사는 아래에서 위로 진행하기 때문)


                # 오프닝, 가시설로 골조공사가 일부구간의 진행이 불가하여 해당 공간을 제외하고 상층부 공사를 진행해야하는 경우 적용방법
                # 지상층 골조가 완료되고 타워크레인이 해체되어야 작업진행 가능
                # 공법에 따라 층간 선후 조건없이 진행할 수 있음(무지주 공법적용시, 데크플레이트),
                # 하루에 여러층 작업 가능
                # 별도의 업무레이어 배정하여 타워크레인 등 오프닝 계획에 반영
                # 예) 3,4,3 그리드에 타워크레인 설치로 오프닝
                # 3,4,3 그리드에는 골조공사 업무레이어, 타워크레인 업무레이어, 오프닝 골조마감 업무레이어 배정
                # 오프닝 골조 마감 업무레이어는 단면상 선후 조건 제외

        # 필연적으로 연속되는 작업
                # if id앞 5자리가 같으면 맨뒤자리 순서에 따라 다음날 작업으로 필히 배정한다.
                # 예) 레미콘타설 후 양생은 필연적인 연속후행관계

        # 전체일정 내 완료 불가시
                # 생산성 조정 알림
                # 조정전 결과 보여주기
                # 추천 생산성 조정 안 1,2,3 보여주기


                ## >>WORK HERE<<
                '''
                Develop your code here.
                Then, run 'test/reschedule.py' to test the code.
                You can find the result directories on 'naviutil.py'
                '''
                "test1"




                ## If all of the constraints are oka, assign the work.
                next_work = remaining_works.pop(0)
                work = Work(grid=grid, day=day, activity=next_work.activity)
                updated_schedule.append(work)
                activity_stack[work.activity.code] += 1
                num_of_assigned_activity += 1

            ## Once every grid passed the work assignment process, move to the next day.
            day += 1
            print(day)

            ## If all activities were assigned to a single work, stop reschduling.
            if num_of_assigned_activity == self.__len__():
                break

        ## TODO: Assign same works to close grids.

        ## TODO: Check activity orders.

        ## TODO: Push some duration-free works to be conducted in the same day.

        ## TODO: Return error if any work remains in local_works.

        ## Update the schedule and sort the grids again.
        self.schedule = updated_schedule
        self.__sort_grids()
        self.__estimate_duration()

        ## TODO: If duration problem occurs, squeeze the schedule.
        if self.duration_expected > self.duration:
            print('INFO: The schedule will be overdue! Please do some actions!')

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
        for day in range(self.duration_expected):
            schedule_dict[day] = {}

        for work in self.schedule:
            schedule_dict[work.day][work.grid.location] = work.activity.code

        schedule_df = pd.DataFrame(schedule_dict)
        return schedule_df

    def export(self, fpath):
        '''
        Export the project schedule in the format of ".xlsx".

        Attributes
        ----------
        fpath : str
            | FilePath for the exported schedule.
        '''

        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        schedule_df = self.schedule2df()
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
        for work in self.schedule:
            if activity_code == work.activity.code:
                here.append(work)

        if verbose:
            print('Fine {}:'.format(activity_code))
            print('  | LOCATION | DAY |')
            for work in sorted(here, key=lambda x:x.day, reverse=False):
                print('  | {:<7} | {:>3} |'.format(work.grid.location, work.day))
        else:
            pass

        return here