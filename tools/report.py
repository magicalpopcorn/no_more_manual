#!python
# -*- coding: utf-8 -*-

import os
import sys
from pprint import pprint

sys.path.insert(0, os.getcwd())

from src.task import Report

report = Report()
result = report.report()
for key, value in result.items():
    pprint(f"{key}: {value}")
