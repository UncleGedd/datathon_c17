from DataLoader import solutionTemplate
import random

def mockSolution():
    solution = solutionTemplate()
    staff = list(solution["Staff"].keys())
    random.shuffle(staff)
    weights = list(random.randrange(i) for i in range(1, len(staff) + 1))
    
    events = solution["Events"].keys()
    for event in events:
        size = random.choices([2, 3], weights=[3, 7])[0]
        pilotsAssigned = random.choices(staff, weights=weights, k=size)
        for pilotAssigned in pilotsAssigned:
            solution["Staff"][pilotAssigned].append(event)
    
    return solution

if __name__ == "__main__":
    # mockSolution()
    from DataLoader import loadPilotData
    import satUtils as util