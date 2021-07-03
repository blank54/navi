#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os


class NaviPath:
    root = os.path.dirname(os.path.abspath(__file__))
    
    fdir_template = os.path.sep.join(root, 'template')
    fdir_component = os.path.sep.join(root, 'component')
    fdir_data = os.path.sep.join(root, 'data')
    fdir_proj = os.path.sep.join(root, 'proj')

    activity_table = os.path.sep.join(fdir_template, 'activity_table.xlsx')
    activity_order = os.path.sep.join(fdir_template, 'activity_order.xlsx')

    navisystem = os.path.sep.join(fdir_component, 'navisystem.pk')

    case_01 = os.path.sep.join(fdir_data, 'case_01.xlsx')
    case_01_schedule = os.path.sep.join(fdir_data, 'case_01_schedule.xlsx')
    case_01_reschedule = os.path.sep.join(fdir_data, 'case_01_reschedule.xlsx')

    case_01_proj = os.path.sep.join(fdir_proj, 'case_01.pk')
