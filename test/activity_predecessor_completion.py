## Print schedule#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os
import sys

rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from copy import deepcopy
import pickle as pk
import pandas as pd
from collections import defaultdict

from naviutil import NaviPath
navipath = NaviPath()

def load_project(case_num):
    with open(navipath.proj(case_num), 'rb') as f:
        project = pk.load(f)

    return project

def calculate_activity_work_plan(schedule):
    work_plan = defaultdict(list)
    for location in schedule:
        for activity_code, day in schedule[location].items():
            work_plan[day].append(activity_code)

    return work_plan

def find_workdays(activity_list, major_code):
    workdays = []
    for activity, day in activity_list.items():
        if major_code in activity:
            workdays.append(day)

    try:
        day_start = min(workdays)
        day_end = max(workdays)
    except ValueError:
        day_start = None
        day_end = None

    return day_start, day_end

def find_upper_location(location):
    x, y, z = location.split('_')
    upper_z = str(int(z) + 1)

    upper_location = '_'.join((x, y, upper_z))
    return upper_location

def find_lower_location(location):
    x, y, z = location.split('_')
    lower_z = str(int(z) - 1 )

    lower_location = '_'.join((x, y, lower_z))
    return lower_location


#9월 11일 주피터로 작업한거 옮겨봅니다. 영향을 받는 그리드 영역 찾기까지 했어요!!!
#predecessor_dist
import pandas as pd
from naviutil import NaviPath
navipath = NaviPath()

activity_pre_dist = pd.read_excel(navipath.activity_pre_dist)

activity_pre_dist.head()


#loading activity dist template and making dic

activity_pre_dist_dic = {}
for _, line in activity_pre_dist.iterrows():
    #    print(line)

    #    print(line['code'])
    #    print(line['predecessor_dist'])
    activity_pre_dist_dic[line['code']] = line['predecessor_dist']

activity_pre_dist_dic
print(activity_pre_dist_dic)


#Loading updated schedule
productivity_updated_schedule = pd.read_excel('D:/cns/navi-master/navi/schedule/schedule_N-05_structure_C-updated_I-062.xlsx')
productivity_updated_schedule



'''COMMENT
현재 코드에서는 schedule을 DataFrame 형태로 사용하고 계시네요. 호환성을 위해, schedule을 읽어오실 땐 아래의 코드를 사용해주시면 좋겠습니다.
단, 실행하기 전에 "run/init.py"를 한번 실행해주셔야 "activity_book.pk"가 정상적으로 작동합니다. (최초 한번만 실행해주시면 됩니다.)

>>>>>>>>>>
from naviutil import NaviFunc
navifunc = NaviFunc()

def import_activity_book():
    try:
        fname_activity_book = 'activity_book.pk'
        with open(os.path.sep.join((navipath.fdir_component, fname_activity_book)), 'rb') as f:
            activity_book = pk.load(f)
    except FileNotFoundError:
        print('Error: You should run "init.py" first to build "activity_book.pk"')

activity_book = import_activity_book()
fpath = 'D:/cns/navi-master/navi/schedule/schedule_N-05_structure_C-updated_I-062.xlsx'
schedule = navifunc.xlsx2schedule(activity_book=activity_book, fname=fname)
<<<<<<<<<<

이렇게 불러온 schedule은 location->day->activity_code로 iterate하는 dictionary입니다.
아래에서 "productivity_updated_schedule.iloc[3][0]"이라고 쓴 코드는 "schedule[특정 location][특정 day]"로 치환할 수 있겠습니다.
이런 방식으로 Line 122-148를 수정해주세요.
'''



#checking activity & dist
productivity_updated_schedule.iloc[3][0]#첫날의 작업 중 첫번째다 치고

check_pre_dist_act = productivity_updated_schedule.iloc[3][0]
checked_dist = activity_pre_dist_dic[check_pre_dist_act] #첫날 첫번째 작업의 선행완료거리값
print(checked_dist)

#grid & activity


# productivity_updated_schedule.columns[0]
#grid_a = productivity_updated_schedule.iloc[3,0] #작업이 있는 첫 그리드를 찾아다 치고
#print(grid_a)


#작업을 가진 그리드 딕셔너리 생성 필요할지는 모르겠음.(현재는 동일 작업으로 함)
act_grids ={}
for grid, activity in productivity_updated_schedule.iterrows():
#     print(activity["Unnamed: 0"]) # grid
#     print(activity[0]) #index
#     print(grid) #index
    grid_list_w_act = {}
    if activity[0] == check_pre_dist_act: #확인된 작업과 동일한 그리드
#         print(activity["Unnamed: 0"])     #확인된 작업과 동일한 그리드 출력
        act_grids[activity["Unnamed: 0"]] = activity[0] #확인된 작업과 동일한 그리드 딕셔너리 생성

print(act_grids)



'''COMMENT
아래의 코드는 불필요하게 반복되는 것 같습니다.
for문은 한번만 돌리면서 x, y, z에 대한 작업을 수행하도록 수정되면 좋을 것 같네요.
Line 187-191을 참고하ㅕ서 for문을 한번만 돌 수 있도록 수정해보시면 좋겠습니다.

이건 그냥 부장님의 코딩 실력 향상을 위한 코멘트이니 바쁘시다면 무시하셔도 괜찮습니다.
'''



#finding grids inside influence of act
# checked_dist값 사용
# print(checked_dist)
# x 영향범위
for grid, activity in act_grids.items():
    x, y, z = grid.split("_")
    pre_dist1 = checked_dist
    pre_dist2 = checked_dist


    x = int(x)
    pre_dist_location_x_list = []
    while pre_dist1 > 0:
        pred_dist_x1 = x + pre_dist1
        #         print(pred_dist_x)
        pre_dist_location_x_list.append(pred_dist_x1)
        pre_dist1 = pre_dist1 - 1

    while pre_dist2 >= 0:
        pred_dist_x2 = x - pre_dist2
        #         print(pred_dist_x)
        if pred_dist_x2 > 0:
            pre_dist_location_x_list.append(pred_dist_x2)
        pre_dist2 = pre_dist2 - 1

    print(pre_dist_location_x_list)

    # y = int(y)
    # ...

    # z = int(z)
    # ...

# checked_dist값 사용
# print(checked_dist)
# y 영향범위
for grid, activity in act_grids.items():
    x, y, z = grid.split("_")
    pre_dist1 = checked_dist
    pre_dist2 = checked_dist
    y = int(y)
    pre_dist_location_y_list = []
    while pre_dist1 > 0:
        pred_dist_y1 = y + pre_dist1
        #         print(pred_dist_y)
        pre_dist_location_y_list.append(pred_dist_y1)
        pre_dist1 = pre_dist1 - 1

    while pre_dist2 >= 0:
        pred_dist_y2 = y - pre_dist2
        #         print(pred_dist_y)
        if pred_dist_y2 > 0:
            pre_dist_location_y_list.append(pred_dist_y2)
        pre_dist2 = pre_dist2 - 1

    print(pre_dist_location_y_list)

# print(checked_dist)
act_checked = productivity_updated_schedule.iloc[3][0]
# print(act_checked)

# Activity code 맨 앞문자
# print(checked_dist)
# z 영향범위

for grid, activity in act_grids.items():
    x, y, z = grid.split("_")
    pre_dist1 = 1
    pre_dist2 = int(-1)
    z = int(z)
    pre_dist_location_z_list = [z]
    if 'D' in act_checked:
        pred_dist_z = z + pre_dist1
        pre_dist_location_z_list.append(pred_dist_z)
    elif 'S' in act_checked:
        pred_dist_z = z + pre_dist2
        pre_dist_location_z_list.append(pred_dist_z)

    print(pre_dist_location_z_list)



'''COMMENT
"location"과 "grid"라는 단어를 사용하는 방식이 저와 조금 다르네요.
저는 'x_y_z'라는 str을 표현할 때는 "location", 어떤 location에서 진행되는 작업들의 딕셔너리는 "grid"로 표현하고 있습니다.

예를 들자면 아래와 같이 사용할 수 있습니다.
>>>>>>>>>>
my_grid = schedule['1_1_2']
activity_code_of_the_grid_on_second_day = my_grid[1] #day는 0부터 시작하니까, 두번째 날의 index는 1입니다.
<<<<<<<<<<

제가 제안한 방식대로라면 아래에서 "##_grid"라고 사용하신 부분은 사실 "##_location"으로 표현해야 합니다.
혹시 다른 의견이 있으시면 말씀해주세요.
제 방식이 괜찮다고 생각되시면, Line 261-283에서 "##_grid"를 모두 "##_location"으로 수정해주시기 바랍니다.
'''



#making influence grid
influence_grids=[]
for x in pre_dist_location_x_list:
    x=str(x)
    for y in pre_dist_location_y_list:
        y=str(y)
        for z in pre_dist_location_z_list:
            z=str(z)
            influence_x_y_z = []
            influence_x_y_z.append(x)
            influence_x_y_z.append(y)
            influence_x_y_z.append(z)
            influence_grid = '_'.join(influence_x_y_z)
            influence_grids.append(influence_grid)

print(influence_grids)

# 자신의 그리드 제거
for grid_except, activity in act_grids.items():
    while grid_except in influence_grids:
        influence_grids.remove(grid_except)

print(influence_grids)



'''COMMENT
여기까지는 잘 진행하신 것 같습니다.
이후로는, 그 위치(location)에서, 그 날(day), 그 작업(activity_code)을 수행할 때, 영향을 받는 위치(influence_grids)에 존재하는 작업들이 모두 완료되었는지를 판별하는 기능을 구현해보시면 어떨까요?
일정을 미루는 것은 그 다음에 진행하시구요.

그런데, "영향을 받는 그리드와 첫날 작업 딕셔너리 만들기"는 사실 어떤 역할을 하는지 잘 이해하지 못 했습니다.
필요하다고 생각되시면 작업 진행해주세요.
제가 코드를 보고 이해해보겠습니다.
'''



#9월 11일
#영향을 받는 그리드와 첫날 작업 디셔너리 만들기
#해당 그리드 작업과 작업 디셔너리내 작업의 선후관계 비교하여 일정 미루기



'''COMMENT
git push 하시기 전에, 코드를 한번 깨끗하게 정리해주시면 훨씬 편하게 읽을 수 있을 것 같습니다.
대단한 작업은 아니고, 불필요한 코드(단순히 결과물을 확인하기 위한 코드, 한번 시도해보는데 사용했지만 최종 실행에는 사용되지 않은 코드 등)는 삭제하고, 줄바꿈(엔터)의 통일성을 맞춰주시는 겁니다.
'''