# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 16:27:08 2020

@author: Supreme
"""

from stkhelper import toolbox
from scheduler import OpenAccess, Schedule

access = OpenAccess('Access\\Access.csv')
schedule = Schedule(access)
for i in range(len(schedule)):
    print(schedule[i])