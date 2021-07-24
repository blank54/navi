import os
import sys

rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])
sys.path.append(rootpath)

from naviutil import NaviPath
navipath = NaviPath()

import pickle as pk

case_num = '01'
with open(navipath.proj(case_num), 'rb') as f:
    project = pk.load(f)

project.export(fpath=navipath.schedule(case_num))



project.reschedule()


project.export(fpath=navipath.reschedule(case_num))