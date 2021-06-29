# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 18:16:48 2020

@author: Ryan Hughes
@email: rh39658@uga.edu
"""
from stkhelper import application, scenario, satellite, sensor, areatarget, toolbox
import os
import scheduler
import power

cwd = os.getcwd()

name = []
latitude = []
longitude = []
ats = []

filename = "SPOC Potential Target List_EastCoast.csv"
openFile = open(filename, "r")
lines = openFile.readlines()
openFile.close()
for line in lines:
    splitLine = line.split(",")
    name.append(splitLine[0])
    latitude.append(splitLine[1])
    longitude.append(splitLine[2])
    
app = application.Application()
scene = scenario.Scenario(app, "SPOCOperational",
                          "4 Dec 2020 12:00:00.000",
                          startTime = "4 Nov 2020 12:00:00.000")
#scene = scenario.Scenario(app, "SPOCOperational",
#                          "4 Feb 2021 12:00:00.000",
#                          startTime = "4 Nov 2020 12:00:00.000")
sun = app.root.ExecuteCommand('New / */Planet Sun')
spoc = satellite.Satellite(scene, "SPOC", 25544)
spoc.SetModel(cwd + "\\SPOC.dae")

spoceye = sensor.Sensor(spoc, 'SPOCeye', (13.93, 13.93))

for i in range(len(name)):
    at = areatarget.AreaTarget(scene,
                               name[i].replace(" ", "_").replace('.',''),
                               [(latitude[i], longitude[i])],
                               radius = 0.001)
    constraints = at.reference.accessConstraints
    sunConstraint = constraints.AddConstraint(58)
    sunConstraint.Min = 5
    ats.append(at)

groundStation = areatarget.AreaTarget(scene,
                                      name="Ground_Station",
                                      coordList=[(33.9487, -83.3754)],
                                      radius=0.001)
constraints = groundStation.reference.accessConstraints
timeConstraint = constraints.AddConstraint(13)
timeConstraint.Min = '00:01:00.000'

app.Connect("SetConstraint */Target/Ground_Station ElevationAngle Min 20.0")

allAccess = []
for i in range(len(ats)):
    access = spoceye.GetAccess(ats[i])
    if (access == 0):
        pass
    else:
        for interval in access:
            newArr = []
            newArr.append(interval[0])
            newArr.append(interval[1])
            newArr.append(ats[i].name)
            allAccess.append(newArr)
            
access = spoc.GetAccess(groundStation)
if (access != 0):
    for interval in access:
        newArr = []
        newArr.append(interval[0])
        newArr.append(interval[1])
        newArr.append(groundStation.name)
        allAccess.append(newArr)
        
allAccess = toolbox.Toolbox.SortAllAccess(allAccess)

accessFile = cwd+'\\Access\\Access.csv'
toolbox.Toolbox.AccessToCSV(allAccess, accessFile)

scheduleArray = scheduler.generateSchedule(accessFile)

scheduleFile = open('schedule.csv','w')
for i in range(len(scheduleArray)):
    scheduleFile.write(scheduleArray[i][0] + "," + \
                       scheduleArray[i][1] + "," + \
                       scheduleArray[i][2] + "," + \
                       scheduleArray[i][3] + "\n")
scheduleFile.close()

powerIntervals = []
openingSchedule = open('schedule.csv', 'r')
scheduleLines = openingSchedule.readlines()
openingSchedule.close()
for line in scheduleLines:
    splitline = line.split(',')
    if splitline[3] == "cruise\n":
        interval = [splitline[0], splitline[1]]
        powerIntervals.append(interval)

counter = 0
for interval in powerIntervals:
    if(interval[0] != ""):
        print(interval[0], interval[1], 60, 0.33, cwd + "\\ActualPower\\Power" + str(counter) + ".csv")
        spoc.GetPower(interval[0], interval[1], 60, 0.33, cwd + "\\ActualPower\\Power" + str(counter) + ".csv")   
        counter += 1

power.combinePowerIntervals(counter)

imageIntervals = []
openSchedule = open('schedule.csv','r')
linesOfSchedule = openSchedule.readlines()
for line in linesOfSchedule:
    splitline = line.split(",")
    if splitline[3] == "imaging\n":
        interval = [splitline[0], splitline[1], splitline[2]]
        imageIntervals.append(interval)







maxElevations = []
for interval in imageIntervals:
    aerList = app.root.ExecuteCommand('AER */Target/%s */Satellite/SPOC TimePeriod "%s" "%s"' % (interval[2], interval[0], interval[1]))
    aers = []
    for i in range(aerList.Count):
        aers.append(aerList.Item(i))
    string = aers[0]
    newString = string.replace("/Application/STK/Scenario/SPOCOperational/Target/Ground_Station /Application/STK/Scenario/SPOCOperational/Satellite/spoc ", "")
    myList = newString.split()
    newList = myList[2:]
    elevations = []
    i = 5
    while i < len(newList):
        elevations.append(float(newList[i]))
        i += 7
    maximum = 0
    for elevation in elevations:
        if elevation > maximum:
            maximum = elevation
    maxElevations.append(maximum)
    
extraCol = []


    
listOfSunElevations = []
for interval in imageIntervals:
    aerSun = app.root.ExecuteCommand('AER */Target/%s */Planet/Sun TimePeriod "%s" "%s"' % (interval[2], interval[0], interval[1]))
    aers = []
    for i in range(aerSun.Count):
        aers.append(aerSun.Item(i))
    string = aers[0]
    sunAerList = string.split(" ")
    newList = sunAerList[2:]
    elevations = []
    i = 5
    while i < len(newList):
        elevations.append(float(newList[i]))
        i += 6
    maximum = 0
    for elevation in elevations:
        if elevation > maximum:
            maximum = elevation
    listOfSunElevations.append(maximum)

finalSchedule = open('schedule.csv', 'w')
counter = 0
for i in range(len(scheduleArray)):
    elevation = "0.0"
    sunElevation = "0.0"
    if (scheduleArray[i][3] == "imaging"):
        elevation = maxElevations[counter]
        sunElevation = listOfSunElevations[counter]
        counter += 1
    finalSchedule.write(scheduleArray[i][0] + "," + \
                       scheduleArray[i][1] + "," + \
                       scheduleArray[i][2] + "," + \
                       scheduleArray[i][3] + "," + \
                       str(elevation) + "," + \
                       str(sunElevation) + "\n")
    
