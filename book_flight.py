# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 21:15:24 2018

@author: X-01
"""

#./book_flight.py --date 2018-04-13 --from BCN --to DUB --one-way
#./book_flight.py --date 2018-04-13 --from LHR --to DXB --return 5
#./book_flight.py --date 2018-04-13 --from NRT --to SYD --cheapest --bags 2
#./book_flight.py --date 2018-04-13 --from CPH --to MIA --fastest

#%% IATA File import

import pandas as pd
import io
import requests
import sys
url = "https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/data/IATA/archives/iata_airport_list_20180210.csv"
s=requests.get(url).content
c=pd.read_csv(io.StringIO(s.decode('utf-8')), sep='^')
airports=c[c["loc_type"]=="A"]
IATA=airports["por_code"]

#%% define command line arguments
import argparse
parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('-f','--from', help='Takeoff airport code (PRG)', required=True)
parser.add_argument('-t','--to', help='Destination airport code (PRG)', required=True)
parser.add_argument('-b','--bags', help='Number of bags',type=int, required=False, default=0)
parser.add_argument('-c','--cheapest', help='Selects cheapest flight',action="store_true", default=True)
parser.add_argument('-s','--fastest', help='Selects fastest flight',action="store_true", default=False)
parser.add_argument('-d','--date', help='Flight date in standart format (2018-01-01)', required=True)
parser.add_argument('-o','--one-way', help='Option if the flight is one way only', action="store_true")
parser.add_argument('-r',"--return", help="Option if flight is one way", action="store", type=int, default=-1)
args = vars(parser.parse_args())

if args["fastest"] :
  args["cheapest"]=False
  b="fastest"
else: 
  b="cheapest"

if args["return"]<0:
    a="one way"
    typeflight="oneway"
    args["return"]=0
else:
    a="returning"
    typeflight="return"

if args["from"] not in list(airports["por_code"]):
    print("The airport " +args["from"]+" does not exist, choose a valid IATA code")
    sys.exit()

if args["to"] not in list(airports["por_code"]):
    print("The airport " +args["to"]+" does not exist, choose a valid IATA code")
    sys.exit()
        


#%% Setting default arguments for testing
#args=dict()
#args["cheapest"] = True
#args["return"] = 0
#args["from"]= "BCN"
#args["to"] = "DUB"
#args["date"] = "2018-04-13"
#args["bags"]=0
#typeflight="oneway"
#b="cheapest"
#a="one way"


# %% Converting to internal variables
from dateutil.parser import parse
from datetime import timedelta

cheapest=args["cheapest"]
flyFrom=args["from"]
to=args["to"]
bags=args["bags"]
dateFrom=parse(args["date"]).strftime('%d/%m/%Y')
returnTo=(parse(args["date"]) + timedelta(days=args["return"])).strftime('%d/%m/%Y')

if args["cheapest"]:
    sort="duration"
else:
    sort="price"

r = ""

if typeflight=="return":
    r = " returning on " + returnTo
if bags>0:
    r=r + " with "+str(bags) + " bags"

print("Checking for "+b+" "+a+" flight from " + 
      str(tuple(airports[IATA==args["from"]]["city_name"])[0]) + " to " 
      + str(tuple(airports[IATA==args["to"]]["city_name"])[0]) + " on " + dateFrom + r
      )

# %% Now finally check the flights

import requests
url="https://api.skypicker.com/flights"

params={"sort":sort,
        "to":to,
        "flyFrom":flyFrom,
        "dateFrom":dateFrom,
        "dateTo":returnTo,
        "asc":1, 
        "limit":1,
        "typeflight":typeflight,
        "v":3
        }

if typeflight=="return":
    params["daysInDestinationFrom"]:args["return"]
    params["daysInDestinationTo"]:args["return"]

response = requests.get(url,params=params)
flight=response.json()["data"][0]

# %% Now Book the flight

print("Search successfull")
print("Booking the " +b+" "+a+" flight from " + flight["cityFrom"] + " to " + flight["cityTo"] + " costing " + str(flight["price"]) + " EUR" )

# I used the check_flights endpoint documentation to make the call. The API is as for now (1:33AM 2018-02-19) Totally unresponsive so supposing that this is correct. 
book_url= "http://128.199.48.38:8080/booking"

params={"booking_token":flight["booking_token"],"bnum":bags}

response = requests.get(book_url,params=params)
