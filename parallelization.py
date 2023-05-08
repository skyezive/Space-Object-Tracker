from sgp4 import exporter
from sgp4.model import Satrec
from astropy.time import Time
import numpy as np
import threading
import importTLE
import time

filename = '10.txt'

with open(filename, "r") as file:
    num_lines = sum(1 for line in file)
    num_tles = round(num_lines/3)

#Set up - fill numpy array with celestrak tles
tle_array = np.empty([num_tles, 2], dtype='U70') #4 tles in .txt, 2 elements per tle
name_array = np.empty([num_tles, 1], dtype='U20')
position_array = np.empty([num_tles, 3])

def serial_start_up():
    counter = 0
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()

            if line[0] != '1' and line[0] != '2':  # isolate the name of the satellite
                sat = list(importTLE.load_gp_from_celestrak(name=line))[0]
                tle = importTLE.extract_tle(sat)
                tle_array[counter] = tle
                name_array[counter] = line
                counter +=1


def read_file(start_line, end_line):
    counter = start_line // 3
    with open(filename, 'r') as file:
        for line_num, line in enumerate(file):
            if start_line <= line_num < end_line:
                line = line.strip()

                if line[0] != '1' and line[0] != '2':
                    sat = list(importTLE.load_gp_from_celestrak(name=line))[0]
                    tle = importTLE.extract_tle(sat)
                    tle_array[counter] = tle
                    name_array[counter] = line
                    counter += 1

def parallel_start_up():
    threads = []
    num_threads = num_tles
    if num_tles > 200:
        num_threads = 200
    batch_size = num_lines // num_threads
    for i in range(num_threads):
        start_line = i * batch_size
        end_line = start_line + batch_size
        if i == num_tles-1:
            end_line = num_lines
        t = threading.Thread(target=read_file, args=(start_line, end_line))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


def update_tle():
    for i in range(num_tles):
        tle_array[i] = exporter.export_tle(list(importTLE.load_gp_from_celestrak(name=name_array[i][0]))[0])
    return tle_array

def serial_get_position():
    for i in range(num_tles):
        #print(tle_array[i])
        if tle_array[i][0] != "":
            satelliteObj = Satrec.twoline2rv(tle_array[i][0], tle_array[i][1]) #convert tle to satrec object
            e, r, v = satelliteObj.sgp4(Time.now().jd1, Time.now().jd2)
            r = [r[i] / 1000 for i in range(3)]
            position_array[i] = r
    return position_array

def get_names():
    counter = 0
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line[0] != '1' and line[0] != '2':  # isolate the name of the satellite
                name_array[counter] = line
                counter +=1
    return name_array

def get_tle():
    TLEcounter = 0
    with open(filename, 'r') as file:
        for line in file:
            #print(line)
            #print(TLEcounter)
            line = line.strip()
            if line[0] != '1' and line[0] != '2':
                pass
            elif line[0] == '1':
                #print(line)
                tle_array[TLEcounter][0] = line
            elif line[0] == '2':
                tle_array[TLEcounter][1] = line
                TLEcounter += 1
    return tle_array
'''
def parallel_get_position(index, position_array):
    if tle_array[i][0] != "":
        satelliteObj = Satrec.twoline2rv(tle_array[i][0], tle_array[i][1]) #convert tle to satrec object
        e, r, v = satelliteObj.sgp4(Time.now().jd1, Time.now().jd2)
        r = [r[i] / 1000 for i in range(3)]
        position_array[index, :] = r
    else:
        print(index)
'''

if __name__ == "__main__":
    #s1 = time.time()
    #parallel_start_up()
    #s2 = time.time()
    #startup_duration = s2-s1
    #print("Parallel Startup duration: {:.4f} seconds".format(startup_duration))
    #s3 = time.time()
    serial_start_up()
    #s4 = time.time()
    #startup_duration2 = s4-s3
    #print("Serial Startup duration: {:.4f} seconds".format(startup_duration2))
    updated_position = np.zeros((num_tles, 3))
    threads = []
    #print(get_tle())


    #run parallel implementation
    #start_parallel_time = time.time()
    #for i in range(num_tles):
        #threads.append(threading.Thread(target=parallel_get_position, args=(i, updated_position)))
        #threads[i].start()
    #for i in range(num_tles):
        #threads[i].join()
    #print(updated_position)
    #end_parallel_time = time.time()
    #parallel_duration = end_parallel_time - start_parallel_time
    #print("Parallel duration: {:.4f} seconds".format(parallel_duration))

    #start_serial_time = time.time()
    #serial_get_position()
    print(serial_get_position())
    #end_serial_time = time.time()
    #serial_duration = end_serial_time - start_serial_time
    #print("Serial duration: {:.4f} seconds".format(serial_duration))






