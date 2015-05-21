import json

import os

class SettingHandler:
    
    def __init__(self, baseDirectory):
        for f in os.listdir(baseDirectory + "/cache"):
            os.remove(baseDirectory + "/cache/" + f)
        filePointer = open(baseDirectory + "settings.json", 'r')
        self.settings = json.loads(filePointer.read())
        filePointer.close()
        filePointer2 = open(baseDirectory + "strings.json", 'r')
        self.strings = json.loads(filePointer2.read())
        filePointer2.close()
        filePointer3 = open(baseDirectory + "names.json", 'r')
        self.names = json.loads(filePointer3.read())
        filePointer3.close()
        filePointer4 = open(baseDirectory + "dataElements.json", 'r')
        self.dataElements = json.loads(filePointer4.read())
        filePointer4.close()
        self.baseDirectory = baseDirectory;
    def getSettings(self):
        return self.settings
    def getDHISUrl(self):
        return self.settings["dhisAPIUrl"]
    def getDHISUserName(self):
        return self.settings["username"]
    def getDHISUserPassword(self):
        return self.settings["password"]
    def getProgram(self,name):
        for program in self.settings["programs"]:
            if program["name"] == name:
                return program
    def getDataElement(self,name):
        for dataElement in self.dataElements:
            if dataElement["name"] == name:
                return dataElement
    def getCoordinates(self):
        return self.settings["coordinates"]
    def setUser(self,json):
        self.user = json
    def getUser(self):
        return self.user
    def getStrings(self):
        return self.strings
    def getNames(self):
        return self.names
    def getBaseDirectory(self):
        return self.baseDirectory