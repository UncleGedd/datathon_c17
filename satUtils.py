import itertools as it
from collections import defaultdict

flightConstraints = {}
flightConstraints["Basic"] = ["MP+","FPC+"]
flightConstraints["Augmented"] = ["MP+","FPQ+","FPC+"]
flightConstraints["AR Augmented"] = ["IP+","MP+","FPC+"]
flightConstraints["SOLL II Augmented"] = ["IP AL+","MP CJ+","FPCCR+"]
flightConstraints["Local"] = ["IP+","FPC+","FPN+"]
flightConstraints["AD Local"] = ["MP C3+","FPQC5+","FPCC5+"]

sim_constraints = defaultdict(dict)
sim_constraints["Day 1"]["min"] = 2 #min number of crew needed
sim_constraints["Day 1"]["max"] = 2 #max number of crew needed
sim_constraints["Day 1"]["crew"] = ["FPL+",""] #crew qualifications needed
sim_constraints["AR Prof"]["min"] = 2 #1 actually
sim_constraints["AR Prof"]["max"] = 2
sim_constraints["AR Prof"]["crew"] = ["",""]
sim_constraints["ISS"]["min"] = 2
sim_constraints["ISS"]["max"] = 2
sim_constraints["ISS"]["crew"] = ["",""]
sim_constraints["G250"]["min"] = 2
sim_constraints["G250"]["max"] = 2
sim_constraints["G250"]["crew"] = ["FPL+",""]
sim_constraints["AL Day 2"]["min"] = 2
sim_constraints["AL Day 2"]["max"] = 2
sim_constraints["AL Day 2"]["crew"] = ["FPL+",""]
sim_constraints["AD Day 2"]["min"] = 2
sim_constraints["AD Day 2"]["max"] = 2
sim_constraints["AD Day 2"]["crew"] = ["MP C3+",""]
sim_constraints["MMP"]["min"] = 2
sim_constraints["MMP"]["max"] = 2 #3 actually
sim_constraints["MMP"]["crew"] = ["FPL+",""] #,""]
sim_constraints["MRP"]["min"] = 2
sim_constraints["MRP"]["max"] = 3
sim_constraints["MRP"]["crew"] = ["FPNC","IP+",""]
sim_constraints["Sim Eval"]["min"] = 2
sim_constraints["Sim Eval"]["max"] = 3
sim_constraints["Sim Eval"]["crew"] = ["FPL+","EP+",""]

requirements = {}
requirements["FPNC"] = ["FPNC"]
requirements[""] = ["FPNC","FPCC","FPKC","FPQC","FPLC","MP C","MP B","IP B","IP A","EP A"]
requirements["FPC+"] = ["FPCC","FPKC","FPQC","FPLC","MP C","MP B","IP B","IP A","EP A"]
requirements["FPQ+"] = ["FPQC","FPLC","MP C","MP B","IP B","IP A","EP A"]
requirements["FPL+"] = ["FPLC","MP C","MP B","IP B","IP A","EP A"]
requirements["MP C+"] = ["MP C","MP B","IP B","IP A","EP A"]
requirements["MP+"] = ["MP C","MP B","IP B","IP A","EP A"]
requirements["IP+"] = ["IP B","IP A","EP A"]
requirements["IP A+"] = ["IP A","EP A"]
# unsure about this
requirements["EP+"] = ["EP A"]
# for now, add this to requirements dict
requirements["FPCCR+"] = ["FPCCR","FPQCR","FPLCR","MP CR","MP CZ","IP BZ"]
requirements["MP CJ+"] = ["MP CJ","IP BJ","IP BX","IP AX"]
requirements["IP AL+"] = ["IP AL","EP AL"]
requirements["MP C3+"] = ["MP C3","MP CZ","MP CJ","MP B3","IP B3","IP B2","IP BZ","IP BJ","IP BX","IP A2","IP AX","IP AL","EP A2","EP AL"]
for req, lst in requirements.items():
    requirements[req] = len(lst[0]), set(lst) 

def validEventId(eventId, scheduledEvents):
    if type(eventId) != str:
        return False, f"Error: invalid eventId '{eventId}'. All eventId's must be a string."
    if not eventId:
        False, f"Error: invalid eventId '{eventId}'. eventId is empty"
    eventType = eventId[0]
    if eventType not in {"s", "f"}:
        return False, f"Error: invalid eventId '{eventId}'. All eventId's must start with 's' or 'f' to indicate 'simulator' or 'flight'."
    index = eventId[1:]
    try:
        index = int(index)
    except ValueError:
        return False, f"Error: invalid eventId '{eventId}'. {index} must be an integer."
    if eventId not in scheduledEvents:
        return False, f"Error: eventID '{eventId}' not found in events."
    return True, ""

def getDurationFromId(eventId, givenEvents):
    event = givenEvents[eventId]
    start = event["StartDay"]
    end = event["EndDay"]
    return end - start

def disjointDatesFromRange(rng):
    disjointDates = []
    if rng:
        orderedDates = sorted(rng, key=lambda a:a[0])
        currentStart, currentEnd = orderedDates[0]
        for start, end in orderedDates[1:]:
            if start > currentEnd:
                disjointDates.append((currentStart, currentEnd))
                currentStart, currentEnd = start, end
            elif end > currentEnd:
                currentEnd = end
        disjointDates.append((currentStart, currentEnd))
    return disjointDates

# Assumes date is in passed in month
def getMonthFromDate(date, monthDateName):
    for (start, end), name in monthDateName:
        if start <= date <= end:
            return name

def fail(message, verbose):
    if verbose:
        print(message)
    return False

# Assumes valid event ID
def eventIdToRequirements(eventId, givenEvents):
    event = givenEvents[eventId]
    return event["CrewMin"], event["CrewMax"], event["CrewRequirements"]

# A pilot's qualification will 
def getQualFromMonth(pilot, month, monthNames, pilots):
    pilotMonthQuals = pilots[pilot]["Quals"]
    # If explicitly defined, return it
    if pilotMonthQuals.get(month):
        return pilotMonthQuals[month]
    # Otherwise, return first qualification or a later one that overrides it, if the later one is >= month
    returnFirst = False
    lastSeen = None
    for monthName in monthNames:
        if pilotMonthQuals.get(monthName):
            qual = pilotMonthQuals[monthName]
            if returnFirst:
                return qual
            lastSeen = qual
        if month == monthName:
            if lastSeen:
                return lastSeen
            returnFirst = True

# Given requirements for mission and crew qualifications, outputs if crew satifies requirement
def satisfiable(reqs, crew):
    assert(len(reqs) == len(crew)), (reqs, crew)
    for crew_perm in it.permutations(crew):
        for i, (member, req) in enumerate(zip(crew_perm, reqs)):
            if not satisfiableMember(req, member):
                break
            if i == len(reqs) - 1:
                return True
    return False

def satisfiableMember(req, member):
    length, satisfiable_qualifications = requirements[req]
    member = member[:length]
    return member in satisfiable_qualifications
