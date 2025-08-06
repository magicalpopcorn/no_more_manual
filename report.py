import io
import subprocess
from pprint import pprint

from PIL import Image

from src.action.report import Report

report = Report()
result = report.report()
for key, value in result.items():
    pprint(f"{key}: {value}")
