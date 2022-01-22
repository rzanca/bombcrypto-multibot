#!/usr/bin/python
from subprocess import Popen

while True:
    print("\nStarting BOT ")
    p = Popen("python index_eng.py", shell=True)
    p.wait() 