"""
Basic setup file for QuestBlue Reports

Created 7-12-23

Alex Marquardt
alex.marquardt@hdtecsolutions.com
"""

import os
import sys

def __find_by_relative_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

cwd = os.getcwd()
log = __find_by_relative_path(cwd + os.sep + 'logs')
output = __find_by_relative_path(cwd + os.sep + 'outputs')
temp = __find_by_relative_path(cwd + os.sep + 'temp')

if not os.path.exists(log):
    os.mkdir(log)
    print("Log file created - % s" %log)

if not os.path.exists(output):
    os.mkdir(output)
    print("Output file created - % s" %output)

if not os.path.exists(temp):
    os.mkdir(temp)
    print("Temp file created - % s" %temp)

input("Press Any Key. . .")
