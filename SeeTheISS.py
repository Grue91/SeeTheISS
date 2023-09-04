#!/usr/bin/env python3

import time
import requests
import platform
import argparse

from math import sin, cos, sqrt, atan2, radians

try:
  import RPi.GPIO as GPIO
  is_pi = True
except (ImportError, RuntimeError):
  is_pi = False

def is_raspberry_pi() -> bool:
    return platform.machine() in ('armv7l', 'armv6l')

#extra check: is it a pi?
is_pi = is_raspberry_pi()


class ISS:
    def __init__(self, cur_lat, cur_lon):
        self.cur_lat = float(cur_lat)
        self.cur_lon = float(cur_lon)
        self.visible = False
        self.update_location()

    def update_location(self):
        loc = ISS_location()
        self.iss_lat = float(loc["iss_position"]["latitude"])
        self.iss_lon = float(loc["iss_position"]["longitude"])
        self.iss_checktime = GetCurrentTime()
        self.iss_distance = self.calculate_distance()

    def calculate_distance(self):
        
        #from stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
        R = 6373.0
        lat1 = radians(self.cur_lat)
        lon1 = radians(self.cur_lon)
        lat2 = radians(self.iss_lat)
        lon2 = radians(self.iss_lon)
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance
    
    @property
    def visible(self):
      return self._visible

    @visible.setter
    def visible(self, state):
      self._visible = state
      if is_pi:
        if state == True:
            GPIO.output(ledPin,GPIO.HIGH)
        if state == False:
            GPIO.output(ledPin,GPIO.LOW)

def ISS_location():
    API_URL = "http://api.open-notify.org/iss-now.json"

    #Make the request
    response = requests.get(API_URL)

    if (response.status_code != 200):
        print("request for IIS data failed")
        exit
    #Unpack results
    ISSData = response.json()
    if ISSData["message"].casefold() == "success".casefold():
        return ISSData
    else:
        print("failed to unpack response")

def GetCurrentTime():
    return time.time()

def Convert_timestamp(timestamp):
    timestamp = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timestamp)

def clear_line():
    #fix after the \r fix for overwriting line
    LINE_CLEAR = '\x1b[2K' # <-- ANSI sequence
    print(end=LINE_CLEAR)

def PeopleInSpace():
    # Get the response from the API endpoint.
    response = requests.get("http://api.open-notify.org/astros.json")
    astronautsdata = response.json()
    #Number of people in Space
    print ("There are currently {} humans in space:\n".format(astronautsdata["number"]))

    for element in astronautsdata["people"]:
        print(element["name"],"-",element["craft"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='SeeTheISS', description='See when the ISS passes by your location')
    parser.add_argument('-conf', '--configuration')           # positional argument
    parser.add_argument('-lat', '--latitude', help="Latitude of your location")      # option that takes a value
    parser.add_argument('-lon', '--longitude', help="Longitude of your location")
    parser.add_argument('-dist', '--distance', default=1000, help="limit of range where you can see the iss")
    parser.add_argument('-led', '--ledpin', default=18, help="if its a raspbberry pi, what, if any, GPIO have you connected the LED to")

    args = parser.parse_args()

    PeopleInSpace()

    if is_pi:
        ledPin = int(args.led)
        #setup for GPIO pin as pin as output
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(ledPin,GPIO.OUT)

    ISS_where = ISS(args.latitude, args.longitude)

    print("\nAs you see, quite a few of them are on the ISS. Want to see it?\n")

    while True:
        ISS_where.update_location()
        if ISS_where.iss_distance <= 8000: #args.dist
            clear_line()
            print("{} - Its here! Go outside and look up".format(Convert_timestamp(GetCurrentTime())))
            
            ISS_where.visible = True
            while ((ISS_where.iss_distance <= 8000) and (ISS_where.visible == True)):
                ISS_where.update_location()
                time.sleep(30)
            ISS_where.visible = False
            print("{} - its gone...".format(Convert_timestamp(GetCurrentTime())))
            Convert_timestamp(GetCurrentTime())
        else:
            print("Wait until the ISS is visible. Its currently {} km away".format(ISS_where.iss_distance), end='\r')
            time.sleep(30)
