from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep

from sgp4 import exporter

import importTLE
from astropy.time import Time

# Creates a default Background Scheduler
sched = BackgroundScheduler()

satellite_dictionary = {}
positionDict = {}
with open('3.txt', 'r') as file:
    for line in file:
        line = line.strip()

        if line[0] != '1' and line[0] != '2': #isolate the name of the satellite
            sat = list(importTLE.load_gp_from_celestrak(name=line))[0]
            satellite_dictionary[line] = sat


def update_tle():
    for key, value in satellite_dictionary.items():
        value = list(importTLE.load_gp_from_celestrak(name=key))[0]
        # print(key)
        # print(exporter.export_tle(value))
        return satellite_dictionary


def update_pv():
    for key, value in satellite_dictionary.items():
        e, r, v = satellite_dictionary[key].sgp4(Time.now().jd1, Time.now().jd2)
        #r = [r[i] / 1000 for i in range(3)]
        print('Satellite Name: ' + str(key), 'Position: ' + str(r), 'Velocity: ' + str(v))
        if e != 0:
            print(e)
        #return satellite_dictionary


def get_position():
    for key, value in satellite_dictionary.items():
        e, r, v = satellite_dictionary[key].sgp4(Time.now().jd1, Time.now().jd2)
        r = [r[i] / 1000 for i in range(3)]
        positionDict[key] = r
    return positionDict
    #print(positionDict)


sched.add_job(update_pv, 'interval', seconds=5)
sched.add_job(get_position, 'interval', seconds=5)
sched.add_job(update_tle, 'interval', days=1)

if __name__ == '__main__':
    # Starts the Scheduled jobs
    sched.start()

    # Runs an infinite loop
    while True:
        sleep(1)
