

import datetime

def get_tasks(file=None, tStart=datetime.datetime.min, tStop=datetime.datetime.max):   
    """Returns list of Task objects containing clock time in range specified.
    
    Takes filename as string and datetime objects as inputs."""
    import re

    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    taskCount = 0
    nonTaskCount = 0
    clockTimeCount = 0

    # ... Ex: * TODO, ** INPROGRESS, and so forth.
    # TODO: read task states in from a config file
    tformat = '%Y-%m-%d %a %H:%M'
    headlinePattern = r'^\s*\*+\s+'
    taskHeadPattern = r'^\s*\*+\s+(EMAIL|READING|TODO|INPROGRESS|WAITING|DONE)\s+(\w+.*)'
    nonTaskHeadPattern = r'^\s*\*+\s+(?!EMAIL|READING|TODO|INPROGRESS|WAITING|DONE)(\w+)'
    timeStamp = r'\[(\d{4}-\d{2}-\d{2}\s+\w{3}\s+\d{1,2}:\d{2})\]'
    clockAmount = r'\s+=>\s+(\d+):(\d{2})\s*'
    clockTimeFront = r'\s*CLOCK:\s+'
    clockTimePattern = ''.join([clockTimeFront, timeStamp, '--', timeStamp, clockAmount])

    taskHeaderList = []
    taskTimeList = []
    taskTimeDeltaList = []
    taskFound = 0
    clockFound = 0

    headlineLoc = [index for index, item in enumerate(lines) if re.match(headlinePattern, item)]
    headlineLocExt = headlineLoc
    headlineLocExt.append(len(lines)-1) # handles case if task is last line
    taskLoc = [[headlineLocExt[hindex], headlineLocExt[hindex+1]] for hindex, hline in enumerate(headlineLoc) if re.match(taskHeadPattern, lines[hline])]

    for (taskBegin, taskEnd)  in taskLoc:
        taskHeadMatch = re.match(taskHeadPattern, lines[taskBegin])
        taskHeaderList.append(taskHeadMatch.groups()[1])
        print 'Task between lines %d and %d is %s\n' % (taskBegin+1, taskEnd+1, taskHeaderList[-1])
        
        tTemp = [];
        dTemp = [];
        for tline in range(taskBegin+1, taskEnd):
            clockMatch = re.match(clockTimePattern, lines[tline])
            if clockMatch:
                taskStart = datetime.datetime.strptime(clockMatch.groups()[0], tformat)
                taskStop = datetime.datetime.strptime(clockMatch.groups()[1], tformat)
                start = taskStart >= tStart
                stop = taskStop <= tStop
                if start and stop:
                    td = taskStop - taskStart
                    tTemp.append([taskStart, taskStop])
                    dTemp.append(td)
                elif (not start) and stop:
                    td = taskStop - tStart
                    tTemp.append([tStart, taskStop])
                    dTemp.append(td)
                elif start and (not stop):
                    td = tStop - taskStart
                    tTemp.append([taskStart, tStop])
                    dTemp.append(td)
                else:
                    pass
        taskTimeList.append(tTemp)
        taskTimeDeltaList.append(dTemp)

    # print 'Found %d task headers\n' % taskCount
    # print 'Found %d non-task headers\n' % nonTaskCount
    # print 'Found %d clock-time headers\n' % clockTimeCount
    return(taskHeaderList, taskTimeList, taskTimeDeltaList)

if __name__ == "__main__":                 
    tBeg = datetime.datetime(2012, 7, 22, 0, 0)
    tEnd = datetime.datetime(2012, 7, 22, 23, 59)
    (taskHeaders, taskTimes, taskTimeDeltas) = get_tasks('example.org', tBeg, tEnd)
    nt = len(taskHeaders)
    print 'get_tasks returned %d tasks' % nt
    ntt = len(taskTimes)
    print 'get_tasks returned %d time pairs' %ntt
    nd = len(taskTimeDeltas)
    print 'get_tasks returned %d deltas' % nd

    for td in taskTimeDeltas:
        print 'Num of clock ins: %d\n' % (len(td))
        for tdelta in td:
            print '%d minutes' % (tdelta.seconds/60)
