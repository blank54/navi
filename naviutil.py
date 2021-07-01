#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os


class NaviPath:
    root = os.path.dirname(os.path.abspath(__file__))
    
    fdir_template = os.path.join(root, 'template/')
    fdir_component = os.path.join(root, 'component')
    fdir_data = os.path.join(root, 'data/')
    fdir_proj = os.path.join(root, 'proj/')

    activity_table = os.path.join(fdir_template, 'activity_table.xlsx')
    activity_order = os.path.join(fdir_template, 'activity_order.xlsx')

    navisystem = os.path.join(fdir_component, 'navisystem.pk')

    case_01 = os.path.join(fdir_data, 'case_01.xlsx')
    case_01_schedule = os.path.join(fdir_data, 'case_01_schedule.xlsx')
    case_01_reschedule = os.path.join(fdir_data, 'case_01_reschedule.xlsx')

    case_01_proj = os.path.join(fdir_proj, 'case_01.pk')
