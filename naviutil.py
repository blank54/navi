#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os


class NaviPath:
    root = '/data/blank54/workspace/project/navi/'
    
    fdir_template = os.path.join(root, 'template/')
    fdir_data = os.path.join(root, 'data/')
    
    activity_list = os.path.join(fdir_template, 'activity_list.xlsx')
    activity_sequence = os.path.join(fdir_template, 'activity_sequence.xlsx')
    productivity_list = os.path.join(fdir_template, 'productivity_list.xlsx')

    activity2code = os.path.join(fdir_template, 'activity2code.json')
    activity2productivity = os.path.join(fdir_template, 'activity2productivity.json')
    activity_tree = os.path.join(fdir_template, 'activity_tree.pk')

    case_01 = os.path.join(fdir_data, 'case_01.xlsx')