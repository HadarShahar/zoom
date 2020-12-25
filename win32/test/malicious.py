from ctypes import *
import time
import subprocess

for i in range(20):
    ok = windll.user32.BlockInput(True)  # enable block

    subprocess.run('taskkill /IM taskmgr.exe')
    time.sleep(1)

ok = windll.user32.BlockInput(False)  # disable block
