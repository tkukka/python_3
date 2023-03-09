#!/usr/bin/python3
# -*- coding: utf-8 -*-
# https://traveling-santa.reaktor.com/

import numpy as np
from copy import deepcopy
R_EARTH = 6378
HOME_ID = 1
ID = 0
LAT = 1
LONG = 2
WEIGHT = 3
MAX_WEIGHT = 10000000 # max 10000 kg = 10 million gramms
START_LAT = 68.073611
START_LONG = 29.315278
FILENAME = 'nicelist.txt'
NEIGHBOR_FILE = 'neighbor.txt'
NEIGHBOR_TOT_FILE = 'neighbor-total.txt'
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
        #return str((self.id, self.latitude, self.longitude, self.weight))
# ----------------------------------------------------------------------
# latitude, longitude, altitude to 3D-vector coordinates
# formula source: ??? differs from e.g. Wikipedia ...        
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
#-------------------------------------------------------------------------
# draw a sphere with nodes       
def visualize(nodes, start_point):
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    
    r = 0.99 # slight shrinkage for the unit sphere to better view the points
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
# read inputted nodes from a file    
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
#def visit_children(v, start_point):
#    t = distance(start_point.xyz, v[0].xyz)
#    if len(v) > 1:
#        for i in range(len(v) - 1):
#            t += distance(v[i].xyz, v[i + 1].xyz)
#            
#    t += distance(start_point.xyz, v[-1].xyz)
#    
#    return t
#-----------------------------------------------------------------------
# edge connects two nodes (children)            
class Edge:
    def __init__(self, c1, c2):
        if c1.id < c2.id:
            self.c = c1, c2
        else:
            self.c = c2, c1
        #self.c2 = c2
        self.dist = distance(c1.xyz, c2.xyz)
        
    def __str__(self):
        return str((self.c[0].id, self.c[1].id))

#    def dist(self):
#        return self.dist
    
#    def vertices(self):
#        return self.c1.id, self.c2.id
    
    def __contains__(self, c):
        return (self.c[0].id == c.id) or (self.c[1].id == c.id)
#------------------------------------------------------------------------
# a sleigh contains the children to be visited and total mass of their
# presents        
class Sleigh:
    def __init__(self):
        self.visit = []
        self.load = 0
        
    def add(self, c):
        
        if c in self.visit:
            return False
        
        if self.load <= (MAX_WEIGHT - c.weight):
            self.visit.append(c)
            self.load += c.weight
            return True
        return False

#    def remove(self, c):
#        if c in self.visit:
#            self.load -= c.weight
#            self.visit.discard(c)
#            return True
#        return False

    def clear(self):
        self.visit.clear()
        
    def status(self):
        print('#children:', len(self.visit), ':', self.load, 'g (', 100 * 
              self.load / MAX_WEIGHT,'%)')
              
#    def fits(self, c):
#        return self.load <= (MAX_WEIGHT - c.weight)
              
#-------------------------------------------------------------------------
class Tour:
    #used_edge_ids = set()
    def __init__(self):
        self.edges = []
        
    def add(self, e):
        if (e not in self.edges):    # and (e.c not in Tour.used_edge_ids):
            self.edges.append(e)
            #Tour.used_edge_ids.add(e.c)
            return True
        
        return False

    def get_cost(self):
        t = 0
        for e in self.edges:
            t += e.dist
        
        return t

#    def remove(self, e):
#        if e in self.edges:
#            #Tour.used_edge_ids.discard(e.c)
#            self.edges.discard(e)
#            return True
#        return False
    # nodes exactly two times in the tour?
    def is_valid(self):
        
        if len(self.edges) == 0:
            return False
        
        a = []
        for e in self.edges:
            c1, c2 = e.c
            a.append(c1.id)
            a.append(c2.id)
        b = np.unique(a, return_counts = True)
        
        return len(b[1]) == len(np.where(b[1] == 2)[0])
#-------------------------------------------------------------------------
#  Geographical clustering using latitude and longitude
#  Map used https://commons.wikimedia.org/w/index.php?curid=168889
GEO_AREAS = ['S-Am S', 'S-Am N', 'N-Am West AA','N-Am west AB', 'N-Am west BA', 
          'N-Am West BB', 'N-Am East AA', 'P-Am East AB', 
          'N-Am East BA', 'N-Am East BB' , 'Afri S', 'Afri N', 'Euro West A',
          'Euro West B', 'Euro East A', 'Euro East B', 'N-Asia', 'S-Asia A', 
          'S-Asia B']

def clusters(data):
    
    print('Clustering...')
    lat = []
    long = []
    
    for c in data: # iterate the children
        lat.append(c.latitude)
        long.append(c.longitude)
    
    lat = np.asarray(lat)
    long = np.array(long)
    
    # now find out nodes for each cluster, plus echo how many there are
    
    c = (((lat > -60) & (lat < -18)) & ((long >= -90) & (long < -30)))
    s_am_s = np.asarray(data)[c ].tolist()
    print('S-Am S', len(s_am_s))

    c = (((lat >= -18) & (lat < 10)) & ((long >= -90) & (long < -30)))
    s_am_n = np.asarray(data)[c ].tolist()
    print('S-Am N', len(s_am_n))

    c = (((lat > 10) & (lat < 38)) & ((long > -170) & (long < -98)))
    n_am_w_aa = np.asarray(data)[c ].tolist()
    print('N-Am West AA', len(n_am_w_aa))

    c = (((lat >= 38) & (lat < 80)) & ((long > -170) & (long < -98)))
    n_am_w_ab = np.asarray(data)[c ].tolist()
    print('N-Am West AB', len(n_am_w_ab))


    c = (((lat > 10) & (lat < 38)) & ((long > -98) & (long < -88)))
    n_am_w_ba = np.asarray(data)[c ].tolist()
    print('N-Am West BA', len(n_am_w_ba))

    c = (((lat >= 38) & (lat < 80)) & ((long > -98) & (long < -88)))
    n_am_w_bb = np.asarray(data)[c ].tolist()
    print('N-Am West BB', len(n_am_w_bb))

    c = (((lat > 10) & (lat < 39)) & ((long >= -88) & (long < -81)))
    n_am_e_aa = np.asarray(data)[c ].tolist()
    print('N-Am East AA', len(n_am_e_aa))
    
    c = (((lat >= 39) & (lat < 80)) & ((long >= -88) & (long < -81)))
    n_am_e_ab = np.asarray(data)[c ].tolist()
    print('N-Am East AB', len(n_am_e_ab))
    
  
    c = (((lat > 10) & (lat < 40)) & ((long >= -81) & (long < -50)))
    n_am_e_ba = np.asarray(data)[c ].tolist()
    print('N-Am East BA', len(n_am_e_ba))
    
    c = (((lat >= 40) & (lat < 80)) & ((long >= -81) & (long < -50)))
    n_am_e_bb = np.asarray(data)[c ].tolist()
    print('N-Am East BB', len(n_am_e_bb))
    
    c = (((lat > -40) & (lat < 5)) & ((long > -20) & (long < 55)))
    afri_s = np.asarray(data)[c ].tolist()
    print('Afri S', len(afri_s))
    
    c = (((lat >= 5) & (lat < 33)) & ((long > -20) & (long < 55)))
    afri_n = np.asarray(data)[c ].tolist()
    print('Afri N', len(afri_n))
    
    c = (((lat >= 33) & (lat < 47)) & ((long >= -50) & (long < 21)))
    europ_w_a = np.asarray(data)[c ].tolist()
    print('Euro West A', len(europ_w_a))
    
    c = (((lat >= 47) & (lat < 80)) & ((long >= -50) & (long < 21)))
    europ_w_b = np.asarray(data)[c ].tolist()
    print('Euro West B', len(europ_w_b))
    
    c = (((lat >= 33) & (lat < 47)) & ((long >= 21) & (long < 60)))
    europ_e_a = np.asarray(data)[c ].tolist()
    print('Euro East A', len(europ_e_a))


    c = (((lat >= 47) & (lat < 80)) & ((long >= 21) & (long < 60)))
    europ_e_b = np.asarray(data)[c ].tolist()
    print('Euro East B', len(europ_e_b))
   
    c = (((lat >= 40) & (lat < 80)) & ((long >= 60) & (long <= 180)))
    n_asia = np.asarray(data)[c ].tolist()
    print('N-Asia ', len(n_asia))
    
    c = (((lat >= -50) & (lat < 40)) & ((long >= 60) & (long < 120)))
    s_asia_1 = np.asarray(data)[c ].tolist()
    print('S-Asia A', len(s_asia_1))    

    c = (((lat >= -50) & (lat < 40)) & ((long >= 120) & (long <= 180)))
    s_asia_2 = np.asarray(data)[c ].tolist()
    print('S-Asia B', len(s_asia_2))

    #manually add
    europ_e_b.append(data[1443]) # North Pole
    
    europ_w_b.append(data[1695]) # 82 -62
    
    europ_w_b.append(data[5944]) # 81 -18
    europ_w_b.append(data[5390]) # 82 -18
    europ_w_b.append(data[7197]) # 82 -18
    
    #S-Am
    s_am_s.append(data[8824]) #South Pole
    s_am_n.append(data[97])   # 0 -90
    s_am_s.append(data[3066])  # -27 -109
    
    s_asia_1.append(data[9618])
    s_asia_2.append(data[4269]) # 180
    s_asia_2.append(data[5847])
    s_asia_2.append(data[9503])
    s_asia_2.append(data[9677])
    s_asia_2.append(data[6931])
    s_asia_2.append(data[8060])
    s_asia_2.append(data[4249])
    s_asia_2.append(data[8415])
    s_asia_2.append(data[8483])
    s_asia_2.append(data[3225])
    s_asia_2.append(data[8864])
    
   
    afri_n.append(data[139])  # 27 56
    afri_n.append(data[8756]) # 24
    afri_n.append(data[5279]) # 24
    afri_n.append(data[3038]) # 24
    afri_n.append(data[797])  # 25
    afri_n.append(data[7954]) # 24
    afri_n.append(data[7769]) # 23
    
    afri_s.append(data[9863]) # -4 55
    afri_n.append(data[8753]) # 17 -25
    afri_n.append(data[5199]) # 15 -23
    afri_n.append(data[1742])
    afri_n.append(data[4044]) # 15  -24
    afri_n.append(data[1807])
    afri_n.append(data[3362])
    afri_n.append(data[513])
    afri_n.append(data[2004]) # 15  -23
    
    afri_n.append(data[249])  # 29 56
    afri_n.append(data[7643]) # 20 56
    afri_n.append(data[4190]) # 23
    afri_n.append(data[695])  # 20
    afri_n.append(data[2424]) # 26
    
    afri_s.append(data[5373]) # -21
    afri_s.append(data[8723]) # -21
    afri_s.append(data[71])   # -20
    afri_s.append(data[5036]) # -20
    
    n_am_w_ab.append(data[3585]) # 70 -179
    n_am_w_ab.append(data[6417]) # 67  -171
    n_am_w_ab.append(data[5576]) 
    n_am_w_ab.append(data[8061]) # 66 -179
    n_am_w_ab.append(data[2709])
    
    # -- checking phase --
    # temporary 
    a = s_am_n + s_am_s + n_am_w_aa + n_am_w_ab + n_am_w_ba + n_am_w_bb + n_am_e_aa \
        + n_am_e_ab +  n_am_e_ba + n_am_e_bb + afri_s + afri_n + europ_w_a + \
        europ_w_b + europ_e_a + europ_e_b + n_asia + s_asia_1 + s_asia_2
    
    b = [] # collect IDs for checking
    for x in a:
        b.append(x.id)

    b = np.unique(b, return_counts = True)
    
    print('Check. All unique? ', len(b[1]) == len(np.where(b[1] == 1)[0]))
    # again, but show duplicates
    if not (len(b[1]) == len(np.where(b[1] == 1)[0])):
        c = np.where(b[1] == 2)[0]
        print(b[0][int(c)])
    
        
    #print(len(c), ' ', len(np.where(b[1] == 2)[0]))
    # verify against all children inputted to the function
    d1 = set(data)
    other = d1 - set(a) # get left overs
    print('Others:', len(other), 'Zero?', len(other) == 0)
#    for x in other:
#        print(x.id, x.latitude, x.longitude, x.weight)
    print()
    return  s_am_s, s_am_n, n_am_w_aa, n_am_w_ab, n_am_w_ba, n_am_w_bb, n_am_e_aa, \
            n_am_e_ab , n_am_e_ba ,n_am_e_bb , afri_s, afri_n, europ_w_a, \
            europ_w_b, europ_e_a, europ_e_b, n_asia, s_asia_1, s_asia_2 
# ----------------------------------------------------------------------    
# Travel nodes in a sleigh and return a tour        
def travel(s, start_point):
    #a = list(s.visit)
    a = s.visit
    #np.random.shuffle(a)
    
    t = Tour()
    e = Edge(start_point, a[0])
    t.add(e)
    for i in range(len(a) - 1):
        e = Edge(a[i], a[i + 1])
        t.add(e)
    e = Edge(a[-1], start_point)
    t.add(e)
    return t    
#--------------------------------------------------------------------------
# input: all children/nodes clustered by geographical location
# output file format:
# ID:  ID ID ID ....
  
MAX_K = 5
def neighbors(area_data):
   
    print()
    print('Neighbors K =', MAX_K)
    out = [] 
    ii = 0
    import csv
    with open(NEIGHBOR_FILE,'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=';')
        
        for a in area_data: # iterate geographical areas
            print(GEO_AREAS[ii])
            ii += 1
           
            for i in range(len(a)): # index children inside the area
                res = []
                if i % 10 == 0:
                    print('.', end='')
                
                for j in range(len(a)): # n x n distance calculations
                    if i != j:
                        d = distance(a[i].xyz, a[j].xyz)
                        res.append( (d,j) )   
                
                t = []
                row = [a[i].id]  # [ID, ID, ID, ...]
                r = sorted(res)[0:MAX_K] 
                for k in r: # iterate tuples of ascending distance
                    t.append(a[k[1]])
                    row.append(a[k[1]].id)
                out.append([a[i], tuple(t)]) # [child, (child, child, ...)]
                filewriter.writerow(row)
                
            print()
    return dict(out)
#------------------------------------------------------------------------- 
# input: all children/nodes, no geographical clustering
# Much hevier distance n x n calculations    
# output file format:
# ID:  ID ID ID ....    
def neighbors_total(data): #  'total' better to be: global? 
    ii = 0
   
    print()
    print('Neighbors (total)')
    #out = [] 
    import csv
    with open(NEIGHBOR_TOT_FILE,'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=';')
            
        for i in range(len(data)):
            ii += 1
            res = []
            if i % 100 == 0:
                print(int(i/100),  end='')
            
            for j in range(len(data)):
                if i != j:
                    d = distance(data[i].xyz, data[j].xyz)
                    res.append((d,j))   
            
            #t = []
            row = [data[i].id]
            r = sorted(res)[0:MAX_K]
            for k in r:
                #t.append(data[k[1]])
                row.append(data[k[1]].id)
            #out.append([a[i], tuple(t)])
            filewriter.writerow(row)
            
        print()
    #return dict(out)    
#-------------------------------------------------------------------------
# read neigbors. count of line items depends on MAX_K    
def read_neigbors(children):
    import csv
    v = []
    print('Neighbors from a file ...', end='')
    with open(NEIGHBOR_FILE) as csvfile:
        filereader = csv.reader(csvfile, delimiter=';')
        for row in filereader:            
            v.append([children[int(row[0]) - 2], 
                               tuple([children[int(row[1]) - 2], 
                                      children[int(row[2]) - 2],
                                      children[int(row[3]) - 2], 
                                      children[int(row[4]) - 2], 
                                      children[int(row[5]) - 2] ]) ])
             
    print('done')
    print()
    return dict(v)         
#--------------------------------------------------------------------------
# read neigbors. count of line items depends on MAX_K 
#  'total' better to be: global? 
def read_neigbors_total(children):
    import csv
    v = []
    print('Neighbors (total) from a file ...', end='')
    with open(NEIGHBOR_TOT_FILE) as csvfile:
        filereader = csv.reader(csvfile, delimiter=';')
        for row in filereader:            
            v.append([children[int(row[0]) - 2], 
                               tuple([children[int(row[1]) - 2], 
                                      children[int(row[2]) - 2],
                                      children[int(row[3]) - 2], 
                                      children[int(row[4]) - 2], 
                                      children[int(row[5]) - 2] ]) ])
             
    print('done')
    print()
    return dict(v)     
#--------------------------------------------------------------------------- 
def solve_old(children, start_point):
#aux = set(children)
#
#while len(aux):
#    
#    s_sleigh = Sleigh()
#    
#    item = aux.pop()
#    s_sleigh.add(item)
#    first = False
#    closest = n[item]
#
#    while not first and len(aux):
#        i = 0
#        ret = False
#        was_full = False
#        while i < MAX_K:
#            item = closest[i]
#            i += 1
#            if item in aux:
#                ret = s_sleigh.add(item)
#                was_full = not ret
#                if ret:
#                    aux.discard(item)
#                    break
#
#
#        # available, didn't fit; ei saatavilla   
#        if ret == False and (not was_full):
#            temp = []
#            while len(aux):
#                item = aux.pop() # aux might be empty?
#                
#                ret = s_sleigh.add(item)
#                if ret:
#                    for a in temp:
#                        aux.add(a)
#                    break
#                temp.append(item)
#            if not ret:
#                was_full = True
#                for a in temp:
#                    aux.add(a)
#                
#        if ret == False and was_full:
#            first = True
#            t_tour = travel(s_sleigh, start_point)
#            count += len(s_sleigh.visit)
#            if t_tour.is_valid():
#                cost = t_tour.get_cost()
#                best = deepcopy(s_sleigh.visit)
#                best_visited.append(best)
#                total += cost
#            
##            if count >= 777 and count <= 895:
##                visualize(s_sleigh.visit, start_point)
#            break
#    
#    if not len(aux):
#        t_tour = travel(s_sleigh, start_point)
#        count += len(s_sleigh.visit)
#        if t_tour.is_valid():
#            cost = t_tour.get_cost()
#            best = deepcopy(s_sleigh.visit)
#            best_visited.append(best)
#            total += cost
#        break    
#    
    return None
#--------------------------------------------------------------------------- 
# awful code...
def solve(children, start_point):
    Q_MAX = 70 # number of tries to build randomly a tour
    areas = clusters(children)

    #visualize(areas[3], start_point)
    #n = neighbors(areas)
    n = read_neigbors(children) # lookup container for the best, close neighbors
    #ntot = read_neigbors_total(children)
    
    tally_best_visited = []  # solution IDs
    best_visited = []        # best tour for a starting child in an area
    total = 0                # distance of tour for a starting child in an area
    tally_total = 0      # solution distance
    tally_count = 0      # sum up processed IDs, for verification
    ii = 0              # just indexing geo.areas
    count = 0 # count children in tours in a geo.area
    #stat_data = []


    for a in areas: # iterate geographical areas
        #np.random.shuffle(a)
        tally_min = 60e6
        print()
        print('Area:', GEO_AREAS[ii])
        
        k = 0
        for start in a: # iteratively pick up first child in the geo.area
            k +=1
            aux = set(a) # make an auxiliary copy of children as a set
            total = 0
            best_visited = []
            count = 0
            #print(type(a))
            init = True
            
        
            first = True
            while len(aux):
                    
                s_sleigh = Sleigh()
        
                #item = aux.pop()
                if init:
                    init=False
                    item = start
                    aux.remove(item)
                else:
                    item = aux.pop()
                s_sleigh.add(item)
                #if len(aux):
                first = False
                
                while not first and len(aux): 
                            
                    closest = n[item]
                    
                    i = 0
                    ret = False
                    was_full = False
                    while i < MAX_K:
                        item = closest[i]
                        i += 1
                        if item in aux:
                            ret = s_sleigh.add(item)
                            was_full = not ret
                            if ret:
                                aux.discard(item)
                                break
                    # 1. available, didn't fit; 2. not available
                    if ret == False and (not was_full):
                        temp = []
                        while len(aux):
                            item = aux.pop() # aux nyt tyhjä?
                            
                            ret = s_sleigh.add(item)
                            if ret:
                                for x in temp:
                                    aux.add(x)
                                break
                            temp.append(item)
                        if not ret:
                            was_full = True
                            for x in temp:
                                aux.add(x)
                            
                    if ret == False and was_full:
                        first = True
                        count += len(s_sleigh.visit)
                        if len(s_sleigh.visit) > 2:
                            t_min = 66e6
                            q = 0
                            while q < Q_MAX:
                                 q += 1
                                 t_tour = travel(s_sleigh, start_point)
                                 if t_tour.is_valid():
                                     cost = t_tour.get_cost()
                                     if  cost < t_min:
                                         t_min = cost
                                         best = deepcopy(s_sleigh.visit)
        #                                     if q > 2:
        #                                         print('jee ')
                                 np.random.shuffle(s_sleigh.visit)
                            total += t_min
                            best_visited.append(best)
                            #stat_data.append([ii, len(best),MAX_WEIGHT-s_sleigh.load, t_min])
                        else:        
                        
                            t_tour = travel(s_sleigh, start_point)
                        
        #                if count >= 1700 and count <= 1726:
        #                    visualize(s_sleigh.visit, start_point)                
        
                            if t_tour.is_valid():
                                cost = t_tour.get_cost()
                                best = deepcopy(s_sleigh.visit)
                                best_visited.append(best)
                                total += cost
                                #stat_data.append([ii, len(best),MAX_WEIGHT-s_sleigh.load, cost])
                        break
                    
                    #aux.discard(item)
                    
            if not len(aux):
                count += len(s_sleigh.visit)
                
                if len(s_sleigh.visit) > 2:
                     t_min = 66e6
                     q = 0
                     while q < Q_MAX:
                         q += 1
                         t_tour = travel(s_sleigh, start_point)
                         if t_tour.is_valid():
                             cost = t_tour.get_cost()
                             if  cost < t_min:
                                 t_min = cost
                                 best = deepcopy(s_sleigh.visit)
    #                                 if q > 1:
    #                                     print('jee ')
                         np.random.shuffle(s_sleigh.visit)
                     total += t_min
                     best_visited.append(best) 
                     #stat_data.append([ii, len(best),MAX_WEIGHT-s_sleigh.load, t_min])
                else:        
                    t_tour = travel(s_sleigh, start_point)
                    if t_tour.is_valid():
                        cost = t_tour.get_cost()
                        best = deepcopy(s_sleigh.visit)
                        best_visited.append(best)
                        total += cost
                        #stat_data.append([ii, len(best),MAX_WEIGHT-s_sleigh.load, cost])
               # break
                
                print()
                #print('IDs status:', count == len(a), ':', count, len(a))
                
                if total < tally_min:
                    tally_min = total
                    tally_best = best_visited
                
                print('Area', ii, 'of', len(areas)-1, 'Best dist:', tally_min, 
                      tally_min / 1e6, 'Mill.km')
                print('Child', k, 'of', len(a), ' Total dist:', total, 
                      total / 1e6, 'Mill.km')
        ii += 1
        tally_total += tally_min
        tally_count += count
        tally_best_visited += tally_best


    print('--- Total:', tally_total, tally_total / 1e6, 'Mill.km')
    print('ID count OK?:', tally_count, tally_count == len(children))
  
    print()
    return tally_total, tally_best_visited
#---------------------------------------------------------------------------     
# ---  main program  ---
def main():

    children = []
    start_point = Child(HOME_ID, START_LAT, START_LONG, 0)

    readfile(FILENAME, children)

    print()
    tally_total, tally_best_visited = solve(children, start_point)
    #neighbors_total(children)
   
    
    if tally_total < 9708746: # the best distance so far
        echo_outfile = True
        print('Got improvement!')
    else:
        echo_outfile = False
        print('No improvement...')
        
    
    if echo_outfile:
        import csv
        print()
        print('======  Solution written to a file  ======')
        with open('output.txt','w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=';')
            filewriter.writerows(tally_best_visited)
        
    print('The End')
 
# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
    