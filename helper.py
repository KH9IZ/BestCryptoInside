import datetime
import time

from main import daily_check

while True:
    clock = str(datetime.datetime.now()).split(' ')[1][:5]
    if clock == '00:00':
        print("start daily")
        daily_check()
        time.sleep(6000)
