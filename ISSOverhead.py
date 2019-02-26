#!/usr/bin/env python3

import time
import requests
import json
import sys

#Current Location:
Lat='59.912157'
Lon='10.750563'

def NextISSPass():
    #CallString
    ApiCall = "http://api.open-notify.org/iss-pass.json?lat={}&lon={}".format(Lat , Lon)

    #Make the request
    response = requests.get(ApiCall)

    #Unpack results
    ISSData = response.json()
    ISSDataResponse = ISSData["response"]
    ISSDataResponse = ISSDataResponse[0]

    ISSDataResponseDuration = ISSDataResponse["duration"]
    ISSDataResponseRiseTime = ISSDataResponse["risetime"]

    #Calculate start and end time of the passing
    #Start time
    unix_timestampStart  = int(ISSDataResponseRiseTime)
    local_time = time.localtime(unix_timestampStart)
    global StartTime
    StartTime = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    #End time
    unix_timestampEnd  = int(ISSDataResponseDuration) + int(ISSDataResponseRiseTime)
    local_time = time.localtime(unix_timestampEnd)
    global EndTime
    EndTime = time.strftime("%Y-%m-%d %H:%M:%S", local_time)

def GetCurrentTime():
    #Get the current localtime
    CurrentTimeUnix = time.time()
    CurrenttimeFormatted = time.localtime(CurrentTimeUnix)
    global CurrentTime
    CurrentTime = time.strftime("%Y-%m-%d %H:%M:%S", CurrenttimeFormatted)

def PeopleInSpace():
    # Get the response from the API endpoint.
    response = requests.get("http://api.open-notify.org/astros.json")
    Astronautsdata = response.json()

    #Number of people in Space
    NumberOfPeopleInSpace = Astronautsdata["number"]
    print ("There are currently",NumberOfPeopleInSpace,"humans in space: \n")

    # List People in Space
    Peopledata = Astronautsdata["people"]

    for element in Peopledata:
        print(element["name"],"-",element["craft"])


NextISSPass()
GetCurrentTime()
PeopleInSpace()

print("As you see, most of them are aboard the ISS. Want to see it?")

while True:

    if CurrentTime >= StartTime:
        print("Look up now!!!", CurrentTime)

        while CurrentTime >= StartTime:
            GetCurrentTime()

            if CurrentTime >= EndTime:
                print("Okay. Its gone now.", CurrentTime)
                NextISSPass()
                GetCurrentTime

    else:
        print("Wait until", StartTime)
        time.sleep(5)
        GetCurrentTime()
