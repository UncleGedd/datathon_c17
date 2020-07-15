import satUtils as util
import json
from collections import defaultdict
from DataLoader import loadPilotData, loadEventData

def checkSchedule(schedulePathOrDict, verbose=True):
    if type(schedulePathOrDict) == str:
        schedulePath = schedulePathOrDict
        try:
            fp = open(schedulePath, "r")
        except Exception as e:
            if verbose:
                print("Error: unable to open file with given path.")
                print(e)
            return False
        try:
            schedule = json.load(fp)
        except Exception as e:
            if verbose:
                print("Error: unable to read json file.")
                print(e)
            return False
        fp.close()
        if verbose:
            print(f"Info: checking schedule found at {schedulePath}.")
    elif type(schedulePathOrDict) == dict:
        schedule = schedulePathOrDict
        if verbose:
            print("Info: checking schedule passed in as dictionary.")
    else:
        return util.fail("Error: first argument to checkSchedule must be a string or dictionary representing a path to a schedule json, or the schedule represented as a dictionary respectively.", verbose)

    pilots = loadPilotData()
    givenEvents = loadEventData()

    monthNames = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    july = (60, 90)
    august = (91, 121)
    september = (122, 151)
    october = (152, 182)
    november = (183, 212)
    december = (213, 243)
    months = [july, august, september, october, november, december]
    july1 = july[0]
    december31 = december[1]
    monthDateName = list(zip(months, monthNames))

    requiredFields = ["Events", "Staff"]
    excludedFields = []
    for field in requiredFields:
        if field not in schedule:
            excludedFields.append(field)
    if excludedFields:
        return util.fail(f"Error: schedule does not include required field(s): {excludedFields}", verbose)

    solutionEvents = schedule["Events"]
    for eventId, startTime in solutionEvents.items():
        validId, message = util.validEventId(eventId, givenEvents)
        if not validId:
            return util.fail(message, verbose)
        try:
            startTime = float(startTime)
        except ValueError:
            return util.fail(f"Error: all events must have an associated start time, which must be a floating point number (e.g. 43653.0). Event {eventId} had start time {startTime}", verbose)
        if not (july1 <= startTime <= december31):
            return util.fail(f"Error: all events must start between July 1, 2019 ({july1}) and December 31, 2019 ({december31}).", verbose)
    if len(solutionEvents) < len(givenEvents) and verbose:
        print(f"Warning: There are {len(solutionEvents)} events scheduled when {len(givenEvents)} were given.")

    eventIdToPeople = defaultdict(list)
    crew = schedule["Staff"]

    # If it's passed in as a json, all of the pilot keys will be strings, so want to convert
    try:
        crew = {int(key): value for key, value in crew.items()}
    except ValueError:
        return util.fail(f"Error: All keys in 'Staff' must be a number, or a string representing a number.", verbose)

    for personId, associatedEvents in crew.items():
        if personId not in pilots:
            return util.fail(f"Error: Person {personId} in 'Staff' field was not found in given pilots.", verbose)
        if type(associatedEvents) != list:
            return util.fail(f"Error: Person {personId} in 'Staff' field was associated with {associatedEvents}, wich is not an array/list", verbose)
        for eventId in associatedEvents:
            # Note: don't need to check eventId validity because we already checked when looping through events
            if eventId not in solutionEvents:
                return util.fail(f"Error: eventId {eventId} in for Pilot {personId} not found in 'Events' field of schedule.", verbose)
            eventIdToPeople[eventId].append(personId)

    satErrors = []
    satWarnings = []

    # Loop again to make sure no person assigned to overlapping events
    for personId, eventIds in crew.items():
        startEndEventList = []
        # Check all events
        for eventId in eventIds:
            start = solutionEvents[eventId]
            end = start + util.getDurationFromId(eventId, givenEvents)
            startEndEventList.append((eventId, (start, end)))
        # Check all scheduled unavailability
        for start, end in util.disjointDatesFromRange(pilots[personId]["Leave"]):
            startEndEventList.append(("Unavailable", (start, end)))
        # Sort assigned events and unavailable dates by start time, then look for overlap
        startEndEventList.sort(key=lambda tup: tup[1][0])
        prevEnd = None
        prevEventId = None
        for eventId, (start, end) in startEndEventList:
            if prevEnd and start <= prevEnd:
                satErrors.append(f"Incorrect Solution Error: {personId} assigned to overlapping events: {prevEventId} and {eventId}.")
            prevEnd = end
            prevEventId = eventId

    # Loop through events to ensure qualifications are met
    for eventId in solutionEvents.keys():
        crew = eventIdToPeople[eventId]
        mn, mx, crewReqs = util.eventIdToRequirements(eventId, givenEvents)
        # print(crew)
        if not (mn <= len(crew) <= mx):
            satErrors.append(f"Incorrect Solution Error: There are {len(crew)} members assigned to {eventId} when there should be between {mn} and {mx} (inclusive).")
            continue
        eventStart = givenEvents[eventId]["StartDay"]
        eventStartMonth = util.getMonthFromDate(eventStart, monthDateName)
        # Get qualifications of each crew member based on month of mission
        crewQuals = [util.getQualFromMonth(member, 
                                           eventStartMonth, 
                                           monthNames, 
                                           pilots) for member in crew]
        if mn <= len(crewQuals) <= mx and len(crewReqs) > len(crewQuals):
            crewReqs = crewReqs[:len(crewQuals)]
        if None in crewQuals or not util.satisfiable(crewReqs, crewQuals):
            satErrors.append(f"Incorrect Solution Error: Event {eventId} with requirements {crewReqs} cannot be satsified by crew members {crew} with qualifications {crewQuals}")

    if satErrors:
        if verbose:
            for errorMessage in satErrors:
                print(errorMessage)
            print()
            print("Incorrect Solution: See error messages above.")
        return False

    if verbose:
        print()
        print("Success: Schedule passed all constraints!")
    return True

if __name__ == '__main__':
    import sys
    import os
    import MockSolution
    folder = "Testing/Schedules/"
    for _ in range(10):
        checkSchedule(MockSolution.mockSolution(), False)
    for filename in os.listdir("./Testing/Schedules"):
        if filename[-4:] == "json":
            print(filename)
            value = checkSchedule(folder + filename)
            expectedValue = True if filename[:3] == "sat" else False
            assert value == expectedValue, f"Expected {expectedValue} for {filename} but got {value}."

            print()
            print()
    print("Passed all test schedules!")
