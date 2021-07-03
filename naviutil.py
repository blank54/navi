#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configuration
import os


class NaviPath:
    root = os.path.dirname(os.path.abspath(__file__))
    
    fdir_template = os.path.sep.join((root, 'template'))
    fdir_component = os.path.sep.join((root, 'component'))
    fdir_data = os.path.sep.join((root, 'data'))
    fdir_proj = os.path.sep.join((root, 'proj'))
    fdir_schedule = os.path.sep.join((root, 'schedule'))

    activity_table = os.path.sep.join((fdir_template, 'activity_table.xlsx'))
    activity_order = os.path.sep.join((fdir_template, 'activity_order.xlsx'))

    navisystem = os.path.sep.join((fdir_component, 'navisystem.pk'))

    def case(self, case_num):
        return os.path.sep.join((self.fdir_data, 'case_{}.xlsx'.format(case_num)))

    def proj(self, case_num):
        return os.path.sep.join((self.fdir_proj, 'proj_{}.pk'.format(case_num)))

    def schedule(self, case_num):
        return os.path.sep.join((self.fdir_schedule, 'schedule_{}_before.xlsx'.format(case_num)))

    def reschedule(self, case_num):
        return os.path.sep.join((self.fdir_schedule, 'schedule_{}_after.xlsx'.format(case_num)))