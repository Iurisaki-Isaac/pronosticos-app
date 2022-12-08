# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 15:36:50 2022

@author: isaac
"""

from datetime import datetime
import time

def isHour(hh,mm):
    return datetime.now().hour == hh and datetime.now().minute == mm

while True:
    if isHour(15,49):
        print("Ya es la hora") # aqui se harían las acciones                
    time.sleep(60)