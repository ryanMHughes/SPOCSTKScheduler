# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 12:52:54 2020

@author: W. Conor McFerren
@email: cnmcferren@gmail.com
"""

def combinePowerIntervals(numIntervals):
    filename = "ActualPower\\Power.csv"
    outputFile = open(filename, 'w')
    for i in range(numIntervals):
        inputFileName = "ActualPower\\Power" + str(i) + ".csv"
        inputFile = open(inputFileName, 'r')
        lines = inputFile.readlines()
        for line in lines[11:]:
            outputFile.write(line)
            
        inputFile.close()
        
    outputFile.close()