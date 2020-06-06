__authors__ = ["Captain Foxtrot#6592", "PH-KDX#4959", "A350Aviator#8582"]

import random # Randomness!
import csv # CSV reader
import datetime
import re # REGEXES ARE FUN! USE REGEXES!
import copy

options = {
    "early": "Earliest",
    "middle": "Middle",
    "late": "Latest",
    "notbothered": "Not bothered"
}

print("FD2S Group Flight Scheduler\n")

''' read the files '''

while True:
    filename = input("File to open (containing sign-ups)\n> ")
    try:
        reader = csv.reader(open(filename), delimiter = ',') # Open the file, read as CSV
        break
    except:
        print("That file doesn't seem to exist! Try again.")
data = [row[1:] for row in reader] # Copy the data

''' sort into people who care and don't care about time '''

timportant = list() # list for people who find time important
tunimportant = list() # list for people who have no commitments

for row in data:
    if row[2] == options["notbothered"]: tunimportant.append(row) 
    else: timportant.append(row) # else if this guy finds time important

''' get peeps into groups '''

# Init the sorted list of people
sortedlist = [list() for _ in range(5)]

# People with commitments
for row in timportant: 
    enum = [options["early"], None, options["middle"], None, options["late"]] # Groups in order
    group = enum.index(row[2]) # Which group are they in?
    sortedlist[group].append(row[0:2]) # Add them to that group

# For people who don't care what time
for row in tunimportant: 
    randindex = random.choice((1, 3)) # Assign them a random group
    sortedlist[randindex].append(row[0:2]) # Add them to that group

result = []
for i in range(len(sortedlist)):
    result.extend(sortedlist[i])

''' command line interface '''

# Converts a time as a string to an array of ints [HH:MM]
toTime = lambda startTime: tuple([int(item) for item in re.split("[:.]", startTime)])

# 2 minute time difference
twoMin = datetime.timedelta(minutes=2)

# Datetime to HH:MM
timeToString = lambda time: "{}:{}".format(str(time.hour).zfill(2), str(time.minute).zfill(2))

# Asks user for the start time and stores it as an array
while True: # Keep looping until the user enters something right

    try: # If the user enters stuff that isn't an int then this'll catch it

        start_time = toTime(input("Start time (format HH:MM; e.g. 16:00))\n> ")) # Prompt

        # If valid
        if start_time[1] < 60 and start_time[1] >= 0 and start_time[0] < 24 and start_time[0] >= 0:
            start_time = datetime.datetime(2000, 1, 1, *start_time)
            break

        else: print("Invalid response - please try again.")

    except: print("Invalid response - please try again.")

# Direction to determine flight level
while True:

    # Prompt
    flightlevel = input("Westbound ('w') or eastbound ('e')?\n> ") 

    # Eastbound: start with odd alt (FL330)
    if flightlevel in ('e', 'E'): 
        start_fl = 330
        break

    # Westbound: start with even alt (FL320)
    elif flightlevel in ('w', 'W'): 
        start_fl = 320
        break

    # they messed up
    else: print("Invalid response - please try again.")

# Extracted data:
# start_time as dict: start_time.hour, start_time.minute
# start_fl as int: 330 or 320

''' now to do some math - fun! '''

# Credit to https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks#comment8550001_1751478
chunks = lambda items: [ items[i:i+4] for i in range(0, len(items), 4)]

# 320, 340, ... , 400
flightlevels = [[None, start_fl + 20 * num, None, None] for num in range(5)]

groups = [copy.copy(flightlevels) for _ in range(int(len(result) / 4) + 1)] # multiple copies of flightlevels, enough to fill up the list of people from result

for num, item in enumerate(groups):
    for subnum, subitem in enumerate(item):
        
        count = 5 * num + subnum
        subcount = num * 4 + subnum
        
        # The last item is always empty, we want to skip it
        if subnum != 4 and subcount < len(result):
            data = result[subcount] # Corresponding person for this index
            groups[num][subnum] = [timeToString(start_time), subitem[1], *data]
        else:
            groups[num][subnum] = [timeToString(start_time), subitem[1], "SLOT", "AVAILABLE"]

        start_time += twoMin

finaloutput = ""

for num, group in enumerate(groups):

    finaloutput += f"GROUP {num+1}\n"

    for pilot in group:
        finaloutput += "{} - FL{}: ".format(*pilot[:2])
        if pilot[2:] == ["SLOT", "AVAILABLE"]: finaloutput += "SLOT AVAILABLE\n"
        else: finaloutput += "@{} {}\n".format(*pilot[2:])

    finaloutput += "\n"

f = open(input("Output filename (This will OVERWRITE the file if it already exists)\n> "), "w")
f.write(finaloutput)
f.close()

print("Success!")
