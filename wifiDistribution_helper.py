# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 18:37:36 2016

@author: Jenni
"""

from gurobipy import *

# -*- coding: utf-8 -*-import re
def parseInput(file_distance , file_ap_to_house , file_existing_ap , file_max_ports, file_blacklist, file_whitelist):
        
    ## PARSE THE DISTANCE ##
        
    # apartments : array to save all the different apartments as a string ----- ['1001', '1002' , '1003' ... ]
        
    # distances : array to save all the distances of an apartment to the other apartments
    # for example: at position 0 a string of distances for the first apartment can be found 
        
    # all_distances_to_apartments : temp variable to store the distance string for each apartment
        
    apartments = []
    distances = []
    all_distances_to_apartments = ""
    
    #### PARSE THE INPUT FILE ####
    
    # for each line in the text file
    for line in file_distance:
        # when the line contains the symbol ":" the apartment number is before this symbol
        if ":" in line:
            
            if all_distances_to_apartments != "":
                # save the whole string for the distances of each apartment
                distances.append(all_distances_to_apartments)
            
            # split the line based on ":" and delete the "-" symbol before the apartment number
            apartment_split = line.split(":")
            one_apartment = apartment_split[0].replace("-" , '')
            
            # save all apartments in the array
            apartments.append( one_apartment )
            
            # string of the first distances
            all_distances_to_apartments = apartment_split[1].replace("\n" , '') 
            
        else:
            
            # extend the string with the remaining distances
            all_distances_to_apartments = all_distances_to_apartments + line.replace("\n" , '')
            
            
    # add the distance of the last apartment in the input file
    distances.append(all_distances_to_apartments)
    
    # dictionary to store for each two apartments the corresponding distance between them
    nachbarn = {}
    
    for index_entry , entry in enumerate(distances):
        # split each distance string
        distance = entry.split(";")
        # remove the last empty element after splitting the "entry"
        del distance[-1]
        
        # iterate through the different distances of one string
        for index_d , d in enumerate(distance):
            # save the distance to the corresponding apartments
            # index_entry : index of the distance string = index of the corresponding apartment 
            # index_d : index of one distance in the distance string = index of the apartment which has the distance d to the apartement with the index index_entry
            nachbarn[apartments[index_entry] , apartments[index_d] ] = d
            
    ## PARSE THE APARTMENT TO HOUSE ##
            
    mapping = {}
    
    for line in file_ap_to_house:
        if ":" in line and not "#" in line:
            mapping_split = line.split(":")
            if mapping_split[0] in mapping:
                mapping[mapping_split[0]].append(mapping_split[1].replace("\n" , '')) 
            else:
                mapping[mapping_split[0]] = [mapping_split[1].replace("\n" , '')]

                
    # Check correctness of the mapping  
    found = False
    for app in apartments:
        for house in mapping:
            if app in mapping[house]:
                found = True
        if found == False:
            print "Apartment " + str(app) + " has no mapping"
            sys.exit(1)
        else:
            found = False
    
    ## PARSE THE EXISTING AP'S
    
    existing_aps = []
    
    for line in file_existing_ap:
        if ":" in line and not "#" in line:
            existing_ap_split = line.split(":")
            existing_aps.append(existing_ap_split[0])
            
    ## PARSE THE MAX MIDSPAN PORTS
            
    max_ports = {}
    
    for line in file_max_ports:
        if ":" in line and not "#" in line:
            max_ports_split = line.split(":")
            max_ports[max_ports_split[0]] = int(max_ports_split[1].replace("\n" , ''))
            
    ## PARSE THE BLACKLIST
            
    blacklist = []
    
    for line in file_blacklist:
        if "," in line and not "#" in line:
            blacklist_split = line.split(",")
            blacklist.append(blacklist_split[0])
            
    # Check if a blacklisted apartment has an existing AP
    for app in apartments:
        if app in blacklist and app in existing_aps:
            print "Apartment " + str(app) + " is blacklisted and has an existing AP"
            sys.exit(1)
                    
    ## PARSE THE WHITELIST
            
    whitelist = []
    
    for line in file_whitelist:
        if "," in line and not "#" in line:
            whitelist_split = line.split(",")
            whitelist.append(whitelist_split[0])
    
    

    return apartments, nachbarn, mapping, existing_aps, max_ports, blacklist, whitelist
