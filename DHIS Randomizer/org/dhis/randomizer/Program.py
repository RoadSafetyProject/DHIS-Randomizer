import HttpRequestor
import json
from datetime import datetime
import random
import os.path
import decimal

global settingHandler
global dhishttpReq
global programHandler
class ProgramHandler:
    dhishttpReq = None
    def __init__(self, settings):
        global settingHandler
        global dhishttpReq
        global programHandler
        programHandler = self
        settingHandler = settings
        dhishttpReq = HttpRequestor.HttpRequestor(settingHandler.getDHISUrl(),settingHandler.getDHISUserName(),settingHandler.getDHISUserPassword());
        resp, content = dhishttpReq.get("programs?filters=type:eq:3&paging=false&fields=id,name,version,programStages[id,version,programStageSections[id],programStageDataElements[sortOrder,dataElement[id,name,code,type,optionSet[id,name,options[id,name],version]]]]")
        js = json.loads(content)
        resp, content = dhishttpReq.get("me")
        settingHandler.setUser(json.loads(content))
        self.programs = []
        self.programDependencies = []
        for p in js["programs"]:
            program = Program(p)
            self.programs.append(program)
            
            depends = []
            settingsProgram = settingHandler.getProgram(program.getName())
            if settingsProgram:
                for depend in settingsProgram["depends"]:
                    depends.append(depend)
            self.programDependencies.append({"name":program.getName(), "dependencies":depends})
    def getNextProgram(self):
        val = 0
        for programDependency in self.programDependencies:
            if len(programDependency["dependencies"]) == 0:
                del self.programDependencies[val]
                return programDependency
            elif self.areDependeciesResolved(programDependency):
                del self.programDependencies[val]
                return programDependency
            val = val + 1
        return None
    def getProgramDependencies(self):
        return self.programDependencies
    def areDependeciesResolved(self,dependencyProgram):
        #print json.dumps(dependencyProgram)
        for dependency in dependencyProgram["dependencies"]:
            for programDependency in self.programDependencies:
                if dependency == programDependency["name"]:
                    #print "False"
                    return False
        #print "True"
        return True
    def getProgram(self,name):
        for program in self.programs:
            if program.getName() == name:
                return program
class Program:
    def __init__(self, program):
        self.data = program
    def getName(self):
        return self.data["name"]
    def getId(self):
        return self.data["id"]
    def randomizeData(self):
        settingProgram = settingHandler.getProgram(self.data["name"])
        numberOfEvents = 100
        if settingProgram:
            numberOfEvents = settingProgram["numberOfEvents"]
        events = []
        for index in range(0,40):
            user = settingHandler.getUser()
            eventDate = self.randomizeDate("1-1-2011","28-12-2015")
            gender = None
            event = {
                     "program" : self.data["id"],
                     "eventDate" :eventDate,
                     "orgUnit": user["organisationUnits"][self.randomizeInteger(0,len(user["organisationUnits"]) - 1)]["id"],
                     "status": "COMPLETED",
                     "storedBy": "admin",
                     "dataValues":[]
                     }
            if settingProgram:
                if "hasCoordinates" in settingProgram:
                    
                    coordinates = settingHandler.getCoordinates()
                    event["coordinate"] = {}
                    event["coordinate"]["latitude"] = str(self.randomizeCoordinates(coordinates["latitude"]["from"],coordinates["latitude"]["to"]))
                    event["coordinate"]["longitude"] = str(self.randomizeCoordinates(coordinates["longitude"]["from"],coordinates["longitude"]["to"]))
            for dataElement in self.data["programStages"][0]["programStageDataElements"]:
                settingDataElement = settingHandler.getDataElement(dataElement["dataElement"]["name"])
                value = None
                if settingDataElement:
                    if "file" in settingDataElement:
                        with open(settingHandler.getBaseDirectory()+ "files/" + settingDataElement["file"],) as json_data:
                            data = json.load(json_data)
                            randomRow = self.randomizeInteger(0, len(data) - 1)
                            value = data[randomRow]
                    elif dataElement["dataElement"]["type"] == "date":
                        value = self.randomizeDate(settingDataElement["range"]["from"],settingDataElement["range"]["to"])
                    elif dataElement["dataElement"]["type"] == "int":
                        value = self.randomizeInteger(settingDataElement["range"]["from"],settingDataElement["range"]["to"])
                        if(settingDataElement["multiple"]):
                            value = value * settingDataElement["multiple"]
                    elif dataElement["dataElement"]["name"] == "First Name":
                        names = settingHandler.getNames();
                        randomRow = self.randomizeInteger(0, len(names) - 1)
                        if(randomRow >= settingDataElement["male"]["from"]):
                            gender = "Male"
                        else:
                            gender = "Female"
                        value = names[randomRow]
                    elif dataElement["dataElement"]["name"] == "Last Name":
                        names = settingHandler.getNames();
                        randomRow = self.randomizeInteger(settingDataElement["male"]["from"], len(names) - 1)
                        value = names[randomRow]
                    elif dataElement["dataElement"]["name"] == "Gender":
                        value = gender
                    else:
                        value = self.randomizeDataElement(dataElement)
                elif dataElement["dataElement"]["name"].startswith( 'Program_' ):
                    events2 = self.getProgramEvents(dataElement["dataElement"]["name"].replace("Program_", ""))
                    if len(events2) != 0:
                        randomRow = self.randomizeInteger(0, len(events2) - 1)
                        value = events2[randomRow]["event"]
                else:
                    if("optionSet" in dataElement["dataElement"]):
                        options = dataElement["dataElement"]["optionSet"]["options"]
                        randomRow = self.randomizeInteger(0, len(options) - 1)
                        value = options[randomRow]["name"]
                    else:
                        value = self.randomizeDataElement(dataElement)
                event["dataValues"].append({"dataElement":dataElement["dataElement"]["id"],"value":value})
            events.append(event)
        sendEvents = {"events" :events}
        #print json.dumps(events)
        resp, content = dhishttpReq.post("events.json",str(json.dumps(sendEvents)))
        return events
    def randomizeDataElement(self,dataElement):
        if dataElement["dataElement"]["type"] == "date":
            value = self.randomizeDate("1-1-2011","1-1-2015")
        elif dataElement["dataElement"]["type"] == "int":
            value = random.randrange(0,1000)
        elif dataElement["dataElement"]["type"] == "bool":
            value = random.randrange(0,1)
            if value == 0:
                value = False
            else:
                value = True
        elif dataElement["dataElement"]["type"] == "string":
            randomStrings = settingHandler.getStrings()
            rowNumber = self.randomizeInteger(0, len(randomStrings))
            value = randomStrings[rowNumber]
        return value
    def randomizeDate(self,start, end):
        """
        This function will return a random datetime between two datetime 
        objects.
        """
        startDate = datetime.strptime(start,'%d-%M-%Y').date()
        endDate = datetime.strptime(end,'%d-%M-%Y').date()
        
        year = random.randint(startDate.year, endDate.year)
         
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        #print "Month1 :" +str(month)
        return datetime(year, month, day).strftime('%Y-%m-%d') #yyyy-MM-dd
    def randomizeInteger(self,start, end):
        if start == end:
            return start
        elif end < 0:
            return 0
        else:
            return random.randrange(start,end)
    def randomizeCoordinates(self,start, end):
        isNegative = False
        if(start < 0 and end < 0):
            start = -1 * start
            end = -1 * end
            isNegative = True
        if isNegative:
            return -1 * decimal.Decimal('%d.%d' % (random.randint(0,start),random.randint(0,end)))
        else:
            return decimal.Decimal('%d.%d' % (random.randint(0,start),random.randint(0,end)))
    def getProgramEvents(self,programName):
        program = programHandler.getProgram(programName.replace("_"," "))
        
        if(not os.path.exists(settingHandler.getBaseDirectory()+ "cache/" + program.getId() + ".program")):
            resp, content = dhishttpReq.get("events?program=" + program.getId())
            events = json.loads(content)
            with open(settingHandler.getBaseDirectory()+ "cache/" + program.getId() + ".program", 'w') as outfile:
                if("events" in events):
                    json.dump(events["events"], outfile)
                    return events["events"]
                else:
                    json.dump([], outfile)
                    return []
        else:
            with open(settingHandler.getBaseDirectory()+ "cache/" + program.getId() + ".program",) as json_data:
                return json.load(json_data)