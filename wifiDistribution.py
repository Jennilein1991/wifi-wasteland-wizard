# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 21:50:37 2016

@author: Jenni
"""

#!/usr/bin/python
from gurobipy import *
## to parse all the txt files
import wifiDistribution_helper
from math import *

# input files
apartment_distance = "app_distance.txt"
apartment_to_house = "app_to_house.txt"
existing_APs = "existing_ap.txt"
max_ports = "max_ports.txt"
blacklist = "blacklist.txt"
whitelist = "whitelist.txt"

#read the files
try:
    # open the text file which maps each apartment to the corresponding distances to each of the other apartments
    # example : -1001:0.0;300.0;1671.096191;1960.24585;
    # apartment 1001 has a distance of 0.0 to itself, 300.0 to the second apartment and so on
    file_distance = open( apartment_distance , "r" )
    file_ap_to_house = open( apartment_to_house , "r" )
    file_existing_ap = open( existing_APs , "r" )
    file_max_ports = open( max_ports , "r" )
    file_blacklist = open( blacklist , "r" )
    file_whitelist = open( whitelist , "r" )
except:
    # file not found, exit program
    print "File not found"
    sys.exit(1)
        
maximalAPNumberInRange = 99 ## maximal number of AP an apartment should have in range
minimalAPNumberInRange = 1 ## minimal
accessPointRange = 701 #7.01m
channelRange = 1000 #10m
neighboursRange = 500 #5m

# parse the input file
(apartments, nachbarn, mapping, existing_aps, max_ports, blacklist, whitelist) = wifiDistribution_helper.parseInput(file_distance , file_ap_to_house , file_existing_ap , file_max_ports, file_blacklist, file_whitelist)


# Mapping of the apartments to the corresponding apartments in range
appInRanges = { app: [] for app in apartments}
for app in apartments:
    for app2 in apartments:
        if float(nachbarn[app , app2]) <= accessPointRange:
            appInRanges[app].append(app2)   
            
# Mapping of the apartments to the corresponding apartments in range for a channel
appInRangesChannel = { app: [] for app in apartments}
for app in apartments:
    for app2 in apartments:
        if float(nachbarn[app , app2]) <= channelRange:
            if app != app2:
                appInRangesChannel[app].append(app2) 
             
# Mapping of the apartments to its neighbours
appAsNeighbour = { app: [] for app in apartments}
for app in apartments:
    for app2 in apartments:
        if float(nachbarn[app , app2]) <= neighboursRange:
            if app != app2:
                appAsNeighbour[app].append(app2)

# Mapping of the apartments to the same floor of a house
floors = { house: [[] for i in range(max(int(app[-3:-2]) + 1 for app in mapping[house])) ] for house in mapping}
for app in apartments:
    for house in mapping:
        if app in mapping[house]:
            if not floors[house][int(app[-3:-2])]:
                floors[house][int(app[-3:-2])] = [app]
            else:
                floors[house][int(app[-3:-2])].append(app) 
                
# Save the optimal value for the amount of AP for one floor in a house
optimalAPinFloor = {}
for house in mapping:
    for floor in floors[house]:
        optimalAPinFloor[house, floors[house].index(floor)] = ceil(max_ports[house] * (float(len(floor)) / float(len(mapping[house]))))   
              
model = Model("wifiDistribution")
# Big M
M = 1000

x = {}
for app in apartments:
    # variable to decide if an apartment has an access point
    x[app] = model.addVar(name="x_" + str(app), vtype= GRB.BINARY , obj = 0.0)

y = {}
for app in apartments:
    # variable to save the amount of access points which are in range
    y[app] = model.addVar(name="y_" + str(app), vtype= GRB.INTEGER , obj = 0.0)  

priority = {}
# DISTANCE TO 2 IN RANGE
# Maximize the sum of all priorities for each apartment
for app in apartments:
    # variable to map a priority to one apartment based on its APs in range
    priority[app] = model.addVar(name="priority_" + str(app), vtype= GRB.INTEGER , obj = 1.0)

amountAPinFloor = {}
# Save the amount of APs in one floor of a house
for house in mapping:
    for floor in floors[house]:
        amountAPinFloor[house, floors[house].index(floor)] = model.addVar(name="amountAPinFloor_" + str(house) + "_" + str(floors[house].index(floor)) , vtype= GRB.INTEGER , obj = 0.0)
  
priorityFloor = {}
# DISTANCE TO THE OPTIMAL AMOUNT OF APS IN ONE FLOOR
# Maximize the sum of all priorities for each floor
for house in mapping:
    for floor in floors[house]:
        # variable to map a priority to one floor based on the amount of APs
        priorityFloor[house, floors[house].index(floor)] = model.addVar(name="priorityFloor_" + str(house) + "_" + str(floors[house].index(floor)) , vtype= GRB.INTEGER , obj = -2.0)
  
amountChannel = 6
channel = {}
for app in apartments:
    for k in range(amountChannel):
        # variable to save if an apartment gets channel k or not
        channel[app, k] =  model.addVar(name="channel_" + str(app) + "_" + str(k), vtype= GRB.BINARY , obj = 0.0)

## ABS FUNCTION FOR RANGE PRIORITY ##
## variables to use decision variables in the abs function. See: https://groups.google.com/forum/#!topic/gurobi/d3q4JWw1ntI ##
p = {}
m = {}
n = {}
z = {}
for app in apartments:
    p[app] = model.addVar(name="p_" + str(app) , vtype= GRB.INTEGER , lb = 0 , obj = 0.0)
for app in apartments:    
    n[app] = model.addVar(name="n_" + str(app) , vtype= GRB.INTEGER , lb = 0 , obj = 0.0)
for app in apartments:    
    m[app] = model.addVar(name="m_" + str(app) , vtype= GRB.BINARY , obj = 0.0)
for app in apartments:    
    z[app] = model.addVar(name="z_" + str(app) , vtype= GRB.INTEGER , obj = 0.0)

model.modelSense = GRB.MAXIMIZE
model.update()

## constraints to use decision variables in the abs function. See: https://groups.google.com/forum/#!topic/gurobi/d3q4JWw1ntI ##
## wanna use: abs(y[app] - 3)
for app in apartments:
    model.addConstr((y[app] - 3) == p[app] - n[app] , name = "substraction_" + str(app))
## either p or n is greater than zero
for app in apartments:
    model.addConstr(p[app] <= M * m[app] , name = "bigM_" + str(app))
for app in apartments:
    model.addConstr(n[app] <= M * (1 - m[app]) , name = "bigM2_" + str(app))
for app in apartments:
    model.addConstr(z[app] == p[app] + n[app] , name = "addition_" + str(app))
## z[app] = abs(y[app] - 3)
for app in apartments:
    model.addConstr(priority[app] == (10 - z[app]) , name = "priority_" + str(app))
   
## The mapping is: range->priority : 0->7 , 1->8 , 2->9 , 3->10 , 4->9 , 5->8 , 6->7 etc..
   
## ABS FUNCTION FOR THE APS PRIORITY FOR EACH FLOOR ##
a = {}
b = {}
c = {}
d = {}
for house in mapping:
    for floor in floors[house]:
        a[house, floors[house].index(floor)] = model.addVar(name="a_" + str(house) + "_" + str(floors[house].index(floor)) , vtype= GRB.INTEGER , lb = 0 , obj = 0.0)
for house in mapping:
    for floor in floors[house]:    
        c[house, floors[house].index(floor)] = model.addVar(name="c_" + str(house) + "_" + str(floors[house].index(floor)) , vtype= GRB.INTEGER , lb = 0 , obj = 0.0)
for house in mapping:
    for floor in floors[house]:   
        b[house, floors[house].index(floor)] = model.addVar(name="b_" + str(house) + "_" + str(floors[house].index(floor)) , vtype= GRB.BINARY , obj = 0.0)
for house in mapping:
    for floor in floors[house]:    
        d[house, floors[house].index(floor)] = model.addVar(name="d_" + str(house) + "_" + str(floors[house].index(floor)) , vtype= GRB.INTEGER , obj = 0.0)

model.modelSense = GRB.MAXIMIZE
model.update()

## constraints to use decision variables in the abs function. See: https://groups.google.com/forum/#!topic/gurobi/d3q4JWw1ntI ##
## wanna use: abs(amountAPinFloor - optimalAPinFloor)
for house in mapping:
    for floor in floors[house]: 
        model.addConstr((amountAPinFloor[house, floors[house].index(floor)] - optimalAPinFloor[house, floors[house].index(floor)]) == a[house, floors[house].index(floor)] - c[house, floors[house].index(floor)] , name = "substraction_" + str(house) + "_" + str(floors[house].index(floor)))
## either a or c is greater than zero
for house in mapping:
    for floor in floors[house]:
        model.addConstr(a[house, floors[house].index(floor)] <= M * b[house, floors[house].index(floor)] , name = "bigM_" + str(house) + "_" + str(floors[house].index(floor)))
for house in mapping:
    for floor in floors[house]:
        model.addConstr(c[house, floors[house].index(floor)] <= M * (1 - b[house, floors[house].index(floor)]) , name = "bigM2_" + str(house) + "_" + str(floors[house].index(floor)))
for house in mapping:
    for floor in floors[house]:
        model.addConstr(d[house, floors[house].index(floor)] == a[house, floors[house].index(floor)] + c[house, floors[house].index(floor)] , name = "addition_" + str(house) + "_" + str(floors[house].index(floor)))
## d[house, floors[house].index(floor)] = abs(amountAPinFloor - optimalAPinFloor)
for house in mapping:
    for floor in floors[house]:
        model.addConstr(priorityFloor[house, floors[house].index(floor)] == d[house, floors[house].index(floor)] , name = "priority_" + str(house) + "_" + str(floors[house].index(floor)))
    

## CONTSRAINTS ##    

# Each apartment which has already an AP -> x[app] = 1
for app in existing_aps:
    model.addConstr(x[app] == 1 , name = "existing_aps_" + str(app))

for app in apartments:
    # each apartment must have at least minimalAPNumberInRange access point in its range
    model.addConstr(y[app] >= minimalAPNumberInRange , name = "minimalRange_" + str(app))

for app in apartments:
    # each apartment must have not more than maximalAPNumberInRange access point in its range
    model.addConstr(y[app] <= maximalAPNumberInRange , name = "maximalRange_" + str(app))
    
for app in apartments:
    # define the amount of AP an apartments has in range
    model.addConstr(y[app] == quicksum(x[app2] for app2 in appInRanges[app]) , name = "y_" + str(app))
    
# no AP in blacklisted apartments
for app in blacklist:
     model.addConstr(x[app] == 0 , name = "x_" + str(app))

# do not pass the maximum ports in a house
for house in max_ports:
    model.addConstr(quicksum(x[app] for app in mapping[house]) <= max_ports[house], name = "maximalPorts_" + str(house))
    
# when an apartment has an accesspoint x[app] = 1 then it exists one channel
# when an apartment has no accesspoint x[app] = 0 then it exists no channel
for app in apartments:
    model.addConstr(quicksum(channel[app, k] for k in range(amountChannel)) == x[app], name = "koppelungChannel_" + str(app) + "_" + str(k))
    
# different channel for access points which are in range of 10m
for app in apartments:
    for app2 in appInRangesChannel[app]:
        for k in range(amountChannel):
            model.addConstr( channel[app, k] + channel[app2, k] <= 1  , name = "differentChannel_" + str(app) + "_" + str(k) + "_" + str(app2))
    
# neighboring apartments should not have both an AP
for app in apartments:
    for app2 in appAsNeighbour[app]:
        model.addConstr( x[app] + x[app2] <= 1  , name = "neighboringApartments_" + str(app) + "_" + str(app2))
    
# minimum amount of APs in one floor
for house in floors:
    for floor in floors[house]:
        model.addConstr( quicksum(x[app] for app in floor) >= min(len(floor) + 1 , 0)  , name = "APsInFloor" + str(house) + "_" + str(floors[house].index(floor)))

# set the amount of aps for one floor = sum of all apartments in the floor
for house in floors:
    for floor in floors[house]:
        model.addConstr( quicksum(x[app] for app in floor) == amountAPinFloor[house, floors[house].index(floor)]  , name = "SetAPsInFloor" + str(house) + "_" + str(floors[house].index(floor)))

            
model.update()    
model.optimize()

## Debug output
for house in floors:
    for floor in floors[house]:
        print "House " + str(house) + ", floor " + str(floors[house].index(floor)) + ":" + str(amountAPinFloor[house, floors[house].index(floor)].x) + "___Optimal:" + str(optimalAPinFloor[house, floors[house].index(floor)]) + "___Abweichung:" + str(priorityFloor[house, floors[house].index(floor)].x)


## Write in file
def writeOutputToFile():
    target = open("output.ini", 'w')
    count = 0
    apartments_temp = apartments[:]
    for app in sorted(apartments_temp):
                if x[app].x == 1 and app not in existing_aps:
                    count = count + 1
                    target.write("[" + str(app) + "]")
                    target.write("\n")
                    target.write("router=1")
                    target.write("\n")
                    target.write("existing=0")
                    target.write("\n")
                    for k in range(amountChannel):
                        if channel[app, k].x == 1:
                            target.write("channel=" + str(k + 1))
                    target.write("\n")
                    target.write("\n")
                if x[app].x == 1 and app in existing_aps:
                    target.write("[" + str(app) + "]")
                    target.write("\n")
                    target.write("router=1")
                    target.write("\n")
                    target.write("existing=1")
                    target.write("\n")
                    for k in range(amountChannel):
                        if channel[app, k].x == 1:
                            target.write("channel=" + str(k + 1))
                    target.write("\n")
                    target.write("\n")
                if x[app].x == 0:
                    target.write("[" + str(app) + "]")
                    target.write("\n")
                    target.write("router=0")
                    target.write("\n")
                    target.write("existing=0")
                    target.write("\n")
                    target.write("channel=-1")
                    target.write("\n")
                    target.write("\n")
    count_zero = 0
    count_one = 0
    count_two = 0
    count_three = 0 
    count_four = 0
    count_five = 0
    for app in apartments:
        if y[app].x == 0:
            count_zero = count_zero + 1
        if y[app].x == 1:
            count_one = count_one + 1
        if y[app].x == 2:
            count_two = count_two + 1
        if y[app].x == 3:
            count_three = count_three + 1
        if y[app].x == 4:
            count_four = count_four + 1
        if y[app].x == 5:
            count_five = count_five + 1
    target.write("Amount range 0: " + str(count_zero))
    target.write("\n")
    target.write("Amount range 1: " + str(count_one))
    target.write("\n")
    target.write("Amount range 2: " + str(count_two))
    target.write("\n")
    target.write("Amount range 3: " + str(count_three))
    target.write("\n")
    target.write("Amount range 4: " + str(count_four))
    target.write("\n")
    target.write("Amount range 5: " + str(count_five))
    target.write("\n")
    
    for house in mapping:
        target.write("\n")
        target.write(str(house) + ":");
        for app in mapping[house]:
            if x[app].x == 1 and app not in existing_aps:
                ## need an AP
                target.write(str(app) + ",");
            
        

writeOutputToFile()
    
 


