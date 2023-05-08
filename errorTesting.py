import csv
import time
import datetime
from astropy.time import Time
from sgp4 import exporter

import updateOrbits

header = ['Satellite Name', 'Time', 'Position', 'Velocity']
tle_dict = updateOrbits.update_tle()

with open('data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for key, value in tle_dict.items():
        writer.writerow([key])
        writer.writerow(exporter.export_tle(value))
    writer.writerow([])
    writer.writerow(header)

while True:
    # Get the current timestamp
    print(datetime.datetime.now())  # .strftime("%Y-%m-%d %H:%M:%S")
    for key, value in tle_dict.items():
        name = key
        e, position, velocity = value.sgp4(Time.now().jd1, Time.now().jd2)

        # Append data to CSV file
        with open('data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, datetime.datetime.now(), position, velocity])

    # print blank line
    with open('data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([])

    # Wait for 30 mins seconds before appending the next row
    time.sleep(1800)

file.close()

'''
import datetime
import math

from astropy.time import Time
from sgp4 import exporter
from sgp4.model import Satrec
import time

import TimeHandlingFunctions
import updateOrbits


now = datetime.datetime.now()
stringTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
objTime = datetime.datetime.now().strptime(stringTime, "%Y-%m-%d %H:%M:%S")


jdate = TimeHandlingFunctions.fnJulianDate(now.year, now.month, now.day, now.hour, now.minute, now.second)
jd = math.floor(jdate + 0.5)
fr = jdate + 0.5 - jd
print(jd,fr)


#testTime = Time.now()
#print(testTime)

'''
'''
sat1 = Satrec.twoline2rv('1 00694U 63047A   23086.63310702  .00006056  00000-0  77329-3 0  9998', '2 00694  30.3574  67.0321 0576541 352.0257   7.1496 14.04852726979511')
sat2 = Satrec.twoline2rv('1 00727U 64001A   23086.87476495  .00000074  00000-0  93905-4 0  9997', '2 00727  69.9052 297.1518 0011340 127.4544 232.7594 13.95483532 12882')
'''
'''
e, position, velocity = sat1.sgp4(Time.now().jd1, Time.now().jd2)
time.sleep(10)
e1, position1, velocity1 = sat1.sgp4(Time.now().jd1, Time.now().jd2)

my_result = tuple(map(lambda i, j: i - j, position, position1))

print(my_result)
'''
