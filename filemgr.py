# Swim Meet file manager
"""
 filemgr.py:  File Management routines for Points Table
         Wayne Reed
         July, 2016

         A Python utility to read and write files for the
         Bluefins swim meet Points Table system
"""
import re
import sys

MULTI_DIMENSION = 1
SINGLE_DIMENSION = 2

CONFIG_DATA = []

def read_file(filename, data_store, dimension):
    """ Read a file into a list """
    try:
        file_descriptor = open(filename, 'r')
        line = file_descriptor.readline()
        while line:
            line = line.strip("\n")
            if dimension == MULTI_DIMENSION:
                fields = re.split(",", line)
                data_store.append(fields)
            elif dimension == SINGLE_DIMENSION:
                data_store.append(line)
            else:
                # return empty data_store as error
                pass
            line = file_descriptor.readline()
        file_descriptor.close()
    except IOError:
        print("file " + filename + " not found")
        sys.exit(2)

def write_file(filename, data_store):
    """ Write a file from a list """
    try:
        file_descriptor = open(filename, 'w')
        for line in data_store:
            file_descriptor.write(line)
            file_descriptor.write('\n')
        file_descriptor.close()
    except IOError:
        print("file " + filename + " could not be opened")
        sys.exit(2)

def get_value(entry):
    """ Get the value of a configuration file entry """
    for file_entry in CONFIG_DATA:
        argument_line = [s for s in file_entry if entry in s]
        if argument_line:
            match = ''.join(argument_line)
            parts = match.split('=')
            if len(parts) == 2:
                return parts[1]
    return  entry + ' not found'
