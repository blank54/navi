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
    fdir_schedule = os.path.sep.join(root, 'schedule')

    activity_table = os.path.sep.join(fdir_template, 'activity_table.xlsx')
    activity_order = os.path.sep.join(fdir_template, 'activity_order.xlsx')

    navisystem = os.path.sep.join(fdir_component, 'navisystem.pk')

    case_01 = os.path.sep.join(fdir_data, 'case_01.xlsx')
    case_01_proj = os.path.sep.join(fdir_proj, 'case_01.pk')
    case_01_schedule = os.path.sep.join(fdir_schedule, 'case_01_schedule.xlsx')
    case_01_reschedule = os.path.sep.join(fdir_schedule, 'case_01_reschedule.xlsx')


def makedir(fpath):
    '''
    A method to make directory for the given file path.

    Attributes
    ----------
    fpath : str
        | A file path.
    '''

    if fpath.endswith(os.path.sep):
        os.makedirs(fpath, exist_ok=True)
    else:
        os.makedirs(os.path.dirname(fpath)), exist_ok=True)