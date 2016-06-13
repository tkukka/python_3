#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright 2016 Tero Kukka. 
# See the license.
R_EARTH = 6371.
R = 1.
FILENAME = 'puzzle.txt'
NAME = 0  # indices
LAT = 1
LONG = 2
ALT = 3

# Satellite. Also applied to the start and the end locations.
# 1. list [] maintains order
# 2. elements in a set are not quaranteed to be in an order. Allows fast membership testing.
#    side-effect: alternative solutions.
class Sat:
    def __init__(self, name, latitude, longitude, altitude):
        self.name = name
        #self.latitude = latitude
        #self.longitude = longitude
        #self.altitude = altitude
        self.xyz = to_xyz(latitude, longitude, altitude)
        #self.visible_objects = set()
        self.visible_objects = []
        
    def add_visible_object(self, obj):
        #self.visible_objects.add(obj)
        self.visible_objects.append(obj)
    def get_visible_objects(self):
        return self.visible_objects
    def remove_visible_objects(self):
        #self.visible_objects = set()
        self.visible_objects = []

# Based on pre-solved intersection between the unit sphere and 
# a parametric 3D line. Assumes X1 != X2 (a real line, not a point)
def solve_intersection(X1, X2):
    dx =  X2[0] - X1[0]
    dy =  X2[1] - X1[1]
    dz =  X2[2] - X1[2]
    x1=X1[0] # just alias
    y1=X1[1]
    z1=X1[2]
    # discriminant value
    D=((2*((x1*dx) + (y1*dy) + (z1*dz)))**2) + (4*(R**2 - x1**2 - y1**2 - z1**2)*(dx**2 + dy**2 + dz**2))
    if D < 0.0:
        return     # no intersection, return None.
    # The line intersects with the sphere. Return parameter values    
    from math import sqrt
    t1 = ((sqrt(D) * -1./ 2.) - (x1*dx) - (y1*dy) - (z1*dz)) / (dx**2 + dy**2 + dz**2)
    t2 = ((sqrt(D) / 2.) - (x1*dx) - (y1*dy) - (z1*dz)) / (dx**2 + dy**2 + dz**2)
    return [t1, t2]

# Convert a latitude, a longitude and an altitude to the spherical coordinates
def to_xyz(lat, long, alt):
    from math import cos, sin, pi
    phi = lat * pi / 180.
    ksi = long * pi / 180.
    x = alt * cos(phi) * cos(ksi)
    y = alt * cos(phi) * sin (ksi)
    z = alt * sin(phi)
    return [x, y, z]

# Line of sight between two locations. True/False.
def los(a, b):
    result = False
    t = solve_intersection(a.xyz, b.xyz)
    
    if t == None:
       result = True # The line between two locations does not intersect with the unit sphere
    elif (t[0] < 0. and t[1] < 0.)  or (t[0] > 1. and t[1] > 1.):
        result = True # The line between two locations  intersects with the unit sphere
                      # but the intersection is not between the two locations
                      # => Earth is not blocking the view.
    return result
   
# Based on Matplotlib Examples: mplot3d Examples: surface3d_demo2.py
# http://matplotlib.org/examples/mplot3d/surface3d_demo2.html
#    zorder has no effect   
def visualize():
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    import numpy as np
    r = 0.99
    fig = plt.figure(figsize=(14, 14))
    ax = fig.add_subplot(111, projection='3d', aspect='equal')
    ax.grid(False)
    # sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = r * np.outer(np.cos(u), np.sin(v))
    y = r * np.outer(np.sin(u), np.sin(v))
    z = r * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, rstride=5, cstride=5, color='w', alpha=0.4, zorder=1)
    # satellites
    i=0
    for s in satellites:
        ax.scatter3D(s.xyz[0], s.xyz[1], s.xyz[2], color='b', zorder=2)
        ax.text3D(s.xyz[0], s.xyz[1], s.xyz[2], i, zorder=2)
        i += 1
    # start
    ax.scatter3D(start_point.xyz[0], start_point.xyz[1], start_point.xyz[2], color='g',zorder=3)
    ax.text3D(start_point.xyz[0], start_point.xyz[1], start_point.xyz[2], 'S', color='g', size=16, zorder=3)
    # end
    ax.scatter3D(end_point.xyz[0], end_point.xyz[1], end_point.xyz[2], color='r', zorder=3)
    ax.text3D(end_point.xyz[0], end_point.xyz[1], end_point.xyz[2], 'E', color='r', size=16, zorder=3)
    # path
    xx=[]; yy=[]; zz=[]
    for s in path:
        xx.append(s.xyz[0]); yy.append(s.xyz[1]); zz.append(s.xyz[2])
    ax.plot(xx, yy, zz, linewidth=2, color='m', zorder=4)
    
    plt.show()

# Find all visible objects. The outcome supports path finding in both ways.
def visibilities():
#    start_point.remove_visible_objects()
#    end_point.remove_visible_objects()
#    for s in satellites:
#        s.remove_visible_objects()
        
    for s in satellites:
        if los(s, start_point):
            start_point.add_visible_object(s)
            s.add_visible_object(start_point)
            
        if los(s, end_point):
            end_point.add_visible_object(s)
            s.add_visible_object(end_point)
            
        for s2 in satellites:
            if s2 is not s and (s not in s2.get_visible_objects()) and los(s, s2):
                s.add_visible_object(s2)
                s2.add_visible_object(s)
                
def print_visibilities():
       print('--- visibilities ---')    
       ss = [start_point]
       for s in satellites:
           ss.append(s)
       ss.append(end_point)
       
       for s in ss:
           print(s.name, ': ', end='')
           tmp = s.get_visible_objects()
           for t in tmp:
               print(t.name, ' ', end='')
           print()

# Breadth-first search. Returns a single path. May not be the shortest.
def find_path():
    from collections import deque
    queue = deque()
    visited = set()    
    path = dict()
    
    path[start_point] = 0
    visited.add(start_point)
    queue.append(start_point)
    exit_loop = False
    while len(queue) > 0 and exit_loop == False:
        s = queue.popleft()
        for n in s.get_visible_objects():
            if n not in visited:
                visited.add(n)
                path[n] = s
                if n == end_point:
                    exit_loop = True
                    break
                queue.append(n)
 # path found   
    queue.clear()
    print('\n----- Path reversed ------')
    n = end_point
    print(end_point.name, ' ', end='')
    queue.appendleft(end_point)
    while (path[n] != 0):
        print(path[n].name, ' ', end='')
        queue.appendleft(path[n])
        n = path[n]
    print()
    return queue

    
# ---  main program  ---
# read the puzzle input file. Scale distances to near value 1.
import csv
satellites = []

with open(FILENAME, newline='') as csvfile:
    filereader = csv.reader(csvfile, delimiter=',')
    for row in filereader:
        if row[NAME].startswith('SAT'):
            s = Sat(row[NAME], float(row[LAT]), float(row[LONG]), (R_EARTH + float(row[ALT])) / R_EARTH)
            satellites.append(s)
        elif row[NAME].startswith('ROUTE'): 
            start_point = Sat('Start', float(row[1]), float(row[2]), 1.0)
            end_point = Sat('End', float(row[3]), float(row[4]), 1.0)

visibilities()
print_visibilities()

path = find_path()
print('\n----- Path ------')
for n in path:
    print(n.name,'', end='')
print()
visualize()
   
