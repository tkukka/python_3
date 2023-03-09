#!/usr/bin/python3
# -*- coding: utf-8 -*-
# https://traveling-santa.reaktor.com/


import numpy as np

R_EARTH = 6378
FILENAME = 'nicelist.txt'
FILE_TO_VERIFY = 'output.txt'
ID = 0
LAT = 1
LONG = 2
WEIGHT = 3
MAX_WEIGHT = 10000000 # max 10000 kg = 10 million gramms
START_LAT = 68.073611
START_LONG = 29.315278
# ----------------------------------------------------------------------
class Child:
    def __init__(self, id, latitude, longitude, weight):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.weight = weight
        self.xyz = to_xyz(latitude, longitude, 1.0)
        
    def __str__(self):
        return str(self.id)
    
# ----------------------------------------------------------------------
# latitude, longitude, altitude to 3D-vector coordinates
def to_xyz(lat, long, alt):
    from math import cos, sin, pi
    from numpy import array
    phi = lat * pi / 180.
    ksi = long * pi / 180.
    x = alt * cos(phi) * cos(ksi)
    y = alt * cos(phi) * sin (ksi)
    z = alt * sin(phi)
    return array([x, y, z])
# ----------------------------------------------------------------------
# https://en.wikipedia.org/wiki/Great-circle_distance#Vector_version
def distance(u, v):
    from math import atan2
    from numpy.linalg import norm
    from numpy import cross, dot
    return R_EARTH * atan2(norm(cross(u,v)), dot(u,v))
# ----------------------------------------------------------------------
# draw a sphere with nodes    
def visualize(nodes, start_point):
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    
    r = 0.99
    fig = plt.figure(figsize = (14, 14))
    ax = fig.add_subplot(111, projection = '3d', aspect = 'equal')
    
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    
    x = r * np.outer(np.cos(u), np.sin(v))
    y = r * np.outer(np.sin(u), np.sin(v))
    z = r * np.outer(np.ones(np.size(u)), np.cos(v))
    
    
    for s in nodes:
        ax.scatter3D(s.xyz[0], s.xyz[1], s.xyz[2], color = 'b')
        ax.text3D(s.xyz[0], s.xyz[1], s.xyz[2], s.id)
       
    
    ax.scatter3D(start_point.xyz[0], start_point.xyz[1], start_point.xyz[2], 
                 color = 'g')
    
    ax.text3D(start_point.xyz[0], start_point.xyz[1], start_point.xyz[2], 'K',
              color = 'g', size = 16)
      
    ax.plot_surface(x, y, z, rstride = 5, cstride = 5, color = 'gray', 
                    alpha = 0.65)
    plt.show()

# ----------------------------------------------------------------------    
def readfile(name, v):
    import csv
    with open(name) as csvfile:
        filereader = csv.reader(csvfile, delimiter=';')
        for row in filereader:
            #i=int(row[ID])
            c = Child(int(row[ID]), float(row[LAT]), float(row[LONG]), 
                      int(row[WEIGHT]))
            
            v.append(c)
# ----------------------------------------------------------------------    
def read_out_file(name, v):
    import csv
    with open(name) as csvfile:
        filereader = csv.reader(csvfile, delimiter=';')
        for row in filereader:
            v2 = [int(i) for i in row]
            v.append(v2)
# ----------------------------------------------------------------------    
# ---  main program  ---
def main():
    children = []
    solution = []
    
    
    start_point = Child(0, START_LAT, START_LONG, 0)
    print('Reading node file:', FILENAME)
    readfile(FILENAME, children)
    print('Reading solution file:', FILE_TO_VERIFY)
    read_out_file(FILE_TO_VERIFY, solution)
    
    
    tally = 0  # total accumulated distance [km]
    ids = []   # collect node IDs
    for s in solution:
        
        t = distance(start_point.xyz, children[s[0] - 2].xyz)
        if len(s) > 1:
            for i in range(len(s) - 1):
                t += distance(children[s[i] - 2].xyz, children[s[i + 1] - 2].xyz)
                
        t += distance(start_point.xyz, children[s[-1] - 2].xyz)
        tally += t
    
        for i in range(len(s)):
            ids.append(children[s[i] - 2].id)
    
    # results
    print('Total distance:', tally, 'km')
    print()
    
    # find out possible duplicate nodes in paths
    b = np.unique(ids, return_counts = True)
    print('#ID:', len(ids))    
    print('All IDs unique? ', len(b[1]) == len(np.where(b[1] == 1)[0]))

#   visualize(children, start_point)

# the shortest distance
#   d = 1500.0
#   for s in children:
#       d1 = distance(start_point.xyz, s.xyz)
#       if d1 < d:
#           d = d1
#           i = s.id
#        
#   print(d)        
      
#   print('Loppu')
# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
