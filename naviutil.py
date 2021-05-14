#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os


class NaviPath:
    root = '/data/blank54/workspace/project/navi/'
    
    fdir_template = os.path.join(root, 'template/')
    fdir_component = os.path.join(root, 'component')
    fdir_data = os.path.join(root, 'data/')
    
    activity_table = os.path.join(fdir_template, 'activity_table.xlsx')
    activity_order = os.path.join(fdir_template, 'activity_order.xlsx')

    activity_tree = os.path.join(fdir_component, 'activity_tree.pk')

    case_01 = os.path.join(fdir_data, 'case_01.xlsx')