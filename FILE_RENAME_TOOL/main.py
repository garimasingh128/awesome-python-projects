#!/usr/bin/env python3

import os
import sys

##########      PREFIX TOBE USED BY NEW FILES ###########
prefix = input("Enter the Prefix- you want to use for each file e.g. nucleus: nucleus-1.jpg, nucleus-2.jpg,... \n")

########## DO NOT CHANGE BELOW, UNTIL YOU ARE A DEVELOPER ;) ############

for count, file in enumerate(os.listdir(sys.argv[1])):

    ###### THIS WILL SEPERATE EXTENSION FROM FILENAME ########
    extnsn = file.split('.')[-1]
    # print(extnsn)

    ###### CHANGE THIS LINE TO MAKE YOUR OWN CONVETION #######
    new_file = prefix+'-'+str(count+1)+'.'+extnsn


    src = sys.argv[1]+file  # SOURCE FILE
    dst = sys.argv[1]+new_file # DESTINATION FILE

    os.rename(src, dst) # ALL MAGIC HERE !!!!!
