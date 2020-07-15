import pandas as pd
from collections import defaultdict

def loadPilotData():
    # Loads All necessary pilot data for the datathon from the Data directory

    qual_paths = [("Data/LetterOfXAug2019.csv", "Aug"),
                  ("Data/LetterOfXSep2019.csv", "Sep"),
                  ("Data/LetterOfXOct2019.csv", "Oct"),
                  ("Data/LetterOfXNov2019.csv", "Nov"),
                  ("Data/LetterOfXDec2019.csv", "Dec")]

    unavailability_path = "Data/Crew Unavailablity.csv"

    STAFF = {}

    # Load Qualifications
    for qual_path, month in qual_paths:
        qual_df = pd.read_csv(qual_path)
        staff_names = list(qual_df['NAME / RANK'])
        quals = list(qual_df['0'])
        for row in range(len(staff_names)):
            staff_id = staff_names[row]
            # Create empty staff if not present
            if staff_id not in STAFF.keys():
                STAFF[staff_id] = _createStaff()

            # Get Qualification for Month
            qual = quals[row]
            STAFF[staff_id]['Quals'][month] = qual


    # Load Unavailability
    unavailability_df = pd.read_csv(unavailability_path)
    staff_names = list(unavailability_df["NAME"])
    start_dates = list(unavailability_df["Start Date"])
    end_dates = list(unavailability_df["End Date"])

    for row in range(len(staff_names)):
        staff_id = staff_names[row]
        # Create empty staff if not present
        if staff_id not in STAFF.keys():
            STAFF[staff_id] = _createStaff()

        # Get Unavailability
        start = start_dates[row] - 43585
        end = end_dates[row] - 43585
        STAFF[staff_id]["Leave"].append([start, end])

    return STAFF


def loadEventData():
    # Loads All necessary pilot data for the datathon from the Data directory

    EVENTS = {}
    local_flights_path = "Data/Local Flights.csv"
    sims_path = "Data/SIMS.csv"

    # Load Local flights
    local_flights_df = pd.read_csv(local_flights_path)
    flight_type = local_flights_df['Type']
    crew_type = local_flights_df['Crew Type']
    start = local_flights_df['Premission Day']
    end = local_flights_df['Postmission']
    air_refueling = local_flights_df['Air Refueling']

    for i in range(len(flight_type)):
        flight_id = "f" + str(i+1)
        crew_min, crew_max, crew_req = _eventRequirements("Local", crew_type[i])

        EVENTS[flight_id] = _createEvent()
        EVENTS[flight_id]['Category'] = "Local"
        EVENTS[flight_id]['Type'] = flight_type[i]
        EVENTS[flight_id]['CrewType'] = crew_type[i]
        EVENTS[flight_id]['StartDay'] = start[i] - 43585
        EVENTS[flight_id]['EndDay'] = end[i] - 43585
        EVENTS[flight_id]['CrewRequirements'] = crew_req
        EVENTS[flight_id]['CrewMin'] = crew_min
        EVENTS[flight_id]['CrewMax'] = crew_max

    # Load Sim Events
    sims_df = pd.read_csv(sims_path)
    sim_type = sims_df['Sim Type']
    start = sims_df['Date']
    end = sims_df['Date']
    for i in range(len(flight_type)):
        sim_id = "s" + str(i+1)
        crew_min, crew_max, crew_req = _eventRequirements("Sim", sim_type[i])

        EVENTS[sim_id] = _createEvent()
        EVENTS[sim_id]['Category'] = "Sim"
        EVENTS[sim_id]['Type'] = sim_type[i]
        EVENTS[sim_id]['StartDay'] = start[i] - 43585
        EVENTS[sim_id]['EndDay'] = end[i] - 43585
        EVENTS[sim_id]['CrewRequirements'] = crew_req
        EVENTS[sim_id]['CrewMin'] = crew_min
        EVENTS[sim_id]['CrewMax'] = crew_max

    return EVENTS


def solutionTemplate():
    # Generates a template for the solution dictionary expected to the scheduling challenge
    SOLUTION = {}
    SOLUTION['Events'] = {}
    SOLUTION['Staff'] = {}

    staff = loadPilotData()
    events = loadEventData()

    # Event Info
    for event_id in events.keys():
        SOLUTION['Events'][event_id] = events[event_id]['StartDay']

    # Pilot Info
    for staff_id in staff.keys():
        SOLUTION["Staff"][staff_id] = []

    return SOLUTION



###########################
#### Helper Functions #####
###########################

def _eventRequirements(category, type):
    sim_constraints = _simConstraintsGen()
    flight_constraints = _fltConstraintsGen()

    # Requirements for Sims
    if category == "Sim":
        simInfo = sim_constraints[type]
        mn = simInfo["min"]
        mx = simInfo["max"]
        crewReqs = simInfo["crew"]
        return mn, mx, crewReqs

    # Requirements for Locals
    if category == "Local":
        crewReqs = flight_constraints[type]
        mn = len(crewReqs)
        mx = len(crewReqs)
        return mn, mx, crewReqs

def _createStaff():
    staff = {}
    staff['Leave'] = []
    staff['Quals'] = {}
    staff['Quals']['Aug'] = None
    staff['Quals']['Sep'] = None
    staff['Quals']['Oct'] = None
    staff['Quals']['Nov'] = None
    staff['Quals']['Dec'] = None
    return staff

def _createEvent():
    event = {}
    event['Category'] = None
    event['Type'] = None
    event['CrewType'] = None
    event['CrewRequirements'] = None
    event['CrewMin'] = None
    event['CrewMax'] = None
    event['StartDay'] = None
    event['EndDay'] = None
    return event

def _fltConstraintsGen():
    flightConstraints = {}
    flightConstraints["Basic"] = ["MP+","FPC+"]
    flightConstraints["Augmented"] = ["MP+","FPQ+","FPC+"]
    flightConstraints["AR Augmented"] = ["IP+","MP+","FPC+"]
    flightConstraints["SOLL II Augmented"] = ["IP AL+","MP CJ+","FPCCR+"]
    flightConstraints["Local"] = ["IP+","FPC+","FPN+"]
    flightConstraints["AD Local"] = ["MP C3+","FPQC5+","FPCC5+"]
    return flightConstraints

def _simConstraintsGen():
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
    sim_constraints["MMP"]["crew"] = ["FPL+",""]; #,""]
    sim_constraints["MRP"]["min"] = 2
    sim_constraints["MRP"]["max"] = 3
    sim_constraints["MRP"]["crew"] = ["FPNC","IP+",""]
    sim_constraints["Sim Eval"]["min"] = 2
    sim_constraints["Sim Eval"]["max"] = 3
    sim_constraints["Sim Eval"]["crew"] = ["FPL+","EP+",""]
    return sim_constraints