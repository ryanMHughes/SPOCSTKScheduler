from stkhelper import toolboximport datetime"""Opens sorted access file and returns arrayParameters:    sortedAccessFile(str): Name of access file to parse    Returns:    accessArray(list): List of access with"""def OpenAccess(sortedAccessFile):    accessFile = open(sortedAccessFile,'r')    lines = accessFile.readlines()        accessArray = []    for i in range(len(lines)):        accessArray.append(lines[i].split(','))            accessFile.close()            return accessArray"""Finds any time conflicts for a possible transition into imaging mode by comparing to other established actionsParameters:    requestedTime(list): A list containing the start and end times (as strings)    actions(list): A list containing all previously established actions    Returns:    boolean: True if there is a conflict. False if there is no conflict."""def FindConflict(requestedTime, actions):    startTime = toolbox.Toolbox.ConvertTime(requestedTime[0])    endTime = toolbox.Toolbox.ConvertTime(requestedTime[1]) + datetime.timedelta(minutes=30)        for i in range(len(actions)):        currentStartTime = toolbox.Toolbox.ConvertTime(actions[i][0])        currentEndTime = toolbox.Toolbox.ConvertTime(actions[i][1])                #check for any time conflicts with pre-existing actions        if ((toolbox.Toolbox.CompareTime(startTime,currentStartTime) and            not toolbox.Toolbox.CompareTime(startTime,currentEndTime)) or                         (toolbox.Toolbox.CompareTime(endTime,currentStartTime) and            not toolbox.Toolbox.CompareTime(endTime,currentEndTime)) or                    (toolbox.Toolbox.CompareTime(currentStartTime,startTime) and            not toolbox.Toolbox.CompareTime(currentStartTime, endTime)) or                        (toolbox.Toolbox.CompareTime(currentEndTime,startTime) and             not toolbox.Toolbox.CompareTime(currentEndTime, endTime))):                return True            return False    """Schedule modes based on the the access that is provided.Scheduling follows the following precedent:    1. Data downlink    2. Imaging + data processing    3. Cruise modeThis means that data downlink is always chosen if the opportunity is given.With data downlink opportunities chosen, the access is parsed and chosen offthe following criteria: if the time of the access plus 30 minutes for a transitionto data processing mode does not conflict with any previously scheduled modes.The remaining time between the modes is automatically scheduled as cruise mode.    Parameters:    accessArray(list): List that contains all sorted access times    Returns:    acceptedActions(list): A list that contains all scheduled mode transitions"""def Schedule(accessArray):    acceptedActions = []    deleteIndices = []    #Find all data downlink times    previousDownlinkStartTime = '5 Nov 2010 12:00:00.000'    for i in range(len(accessArray)):        if (accessArray[i][2].replace('\n','') == 'Ground_Station'):            timeDelta = abs(toolbox.Toolbox.GetTimeDelta([accessArray[i][0], previousDownlinkStartTime]))            if(timeDelta < 86400.0):                deleteIndices.append(i)            else:                acceptedActions.append([accessArray[i][0],                                    accessArray[i][1],                                    accessArray[i][2].replace('\n',''),                                    'data_downlink'])                previousDownlinkStartTime = accessArray[i][0]                deleteIndices.append(i)            #for i in range(len(accessArray)):        #if (accessArray[i][2].replace('\n','') == 'Ground_Station'):            #acceptedActions.append([accessArray[i][0],                                   # accessArray[i][1],                                    #accessArray[i][2].replace('\n',''),                                    #'data_downlink'])           # deleteIndices.append(i)          #remove data downlink times from future consideration    for i in range(len(deleteIndices)):        del accessArray[deleteIndices[len(deleteIndices)-1-i]]        deleteIndices = []    #find non-conflicting access    for i in range(len(accessArray)):        conflict = FindConflict((accessArray[i][0],accessArray[i][1]),acceptedActions)        if not conflict:            acceptedActions.append([accessArray[i][0],                                    accessArray[i][1],                                    accessArray[i][2].replace('\n',''),                                    'imaging'])            deleteIndices.append(i)        else:            deleteIndices.append(i)                #remove imaging times from future consideration    for i in range(len(deleteIndices)):        del accessArray[deleteIndices[len(deleteIndices)-1-i]]        print(acceptedActions)    actionsLength = len(acceptedActions)    acceptedActions = toolbox.Toolbox.SortAllAccess(acceptedActions)    i = 0    while i < (actionsLength - 1):        if (                (acceptedActions[i][1] != acceptedActions[i+1][0]) and                 (toolbox.Toolbox.CompareTime(toolbox.Toolbox.ConvertTime(acceptedActions[i+1][0]), toolbox.Toolbox.ConvertTime(acceptedActions[i][0])))            ):            acceptedActions.append([acceptedActions[i][1],                                    acceptedActions[i+1][0],                                    "NA",                                    "cruise"])                i += 1            return toolbox.Toolbox.SortAllAccess(acceptedActions)def generateSchedule(accessFile):    access = OpenAccess(accessFile)    schedule = Schedule(access)    return schedule