
import sys
import getopt
import datetime
import pylab

def get_tasks(filename=None, tStart=datetime.datetime.min, tStop=datetime.datetime.max):   
    """Returns list of Task objects containing clock time in range specified.
    
    Takes filename as string and datetime objects as inputs."""
    import re

    try:
        f = open(filename, 'r')
    except IOError as e:
        print 'I/O error({0}): {1}'.format(e.errno, e.strerror)
    else:
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
                    if taskStop > tStart:
                        td = taskStop - tStart
                        tTemp.append([tStart, taskStop])
                        dTemp.append(td)
                elif start and (not stop):
                    if tStop > taskStart:
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

def sum_deltas(ltimes=None):
    """Sum list of timedelta objects"""
    import datetime
    tsum = datetime.timedelta(0)
    for td in ltimes:
        tsum = tsum + td
    return tsum

def usage():
    print 'Usage: pyreport [OPTION] files ...\nTry \'pyreport --help\' for more infomration'

def main(argv):
    try:
        opts, fileList = getopt.getopt(argv, 'b:e:t:h:', ['begin-date', 'end-date', 'tags', 'help'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    tBeg = datetime.datetime.min # default is beginning of time (all records)
    tEnd = datetime.datetime.max # default is end of time (all records)
    dformat = '%Y-%m-%d'
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-b', '--begin-date'):
            dBeg = datetime.datetime.strptime(arg, dformat)
            dtime = datetime.time(0, 0)
            tBeg = datetime.datetime.combine(dBeg, dtime)
        elif opt in ('-e', '--end-date'):
            dEnd = datetime.datetime.strptime(arg, dformat)
            dtime = datetime.time(23, 59)
            tEnd = datetime.datetime.combine(dEnd, dtime)
    
    print 'Remaining arguments: %d' % (len(fileList))
    if len(fileList) == 0:
        print 'Missing filename parameters'
        sys.exit(3)

    for f in fileList:
        (taskHeaders, taskTimes, taskTimeDeltas) = get_tasks(f, tBeg, tEnd)
        clockTimeDeltaSum = [sum_deltas(tdlist) for tdlist in taskTimeDeltas]
        clockMinutes = [ct.seconds/60 for ct in clockTimeDeltaSum]

        pylab.pie(clockMinutes, labels=taskHeaders)

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

if __name__ == "__main__":                 
    main(sys.argv[1:])
