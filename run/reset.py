#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import shutil

import os
rootpath = os.path.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1])

import sys
sys.path.append(rootpath)
from naviutil import NaviPath
navipath = NaviPath()


def do_reset():
    reset_dirs = [navipath.fdir_component, 
                  navipath.fdir_proj, 
                  navipath.fdir_schedule,]

    print('==================================================')
    print('RESET workspace')
    for dir in reset_dirs:
        try:
            shutil.rmtree(dir)
            print('  | Reset: {}'.format(dir))
        except FileNotFoundError:
            print('  | No File or Directory: {}'.format(dir))


if __name__ == '__main__':
    do_reset()