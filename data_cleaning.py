def get_invalid_leave(pilots):
    invalid_leave = {}
    for p in pilots.keys():
        for l in pilots[p]['Leave']:
            for day in l:
                if day < 0:
                    invalid_leave[p] = pilots[p]
    return invalid_leave

def clean_invalid_leave(pilots):
    invalid_leave = get_invalid_leave(pilots)
    for p in invalid_leave: 
        for i, l in enumerate(pilots[p]['Leave']):
            for j, day in enumerate(l):
                if day < 0:
                    if j == 1:  
                        pilots[p]['Leave'][i][j] = l[j-1]
    return pilots

quals_map = {'IPA2': 'IP A2',
             'FPKN': 'FPKA',
             'UP A': 'IP A',
             'MPCR': 'MP CR',
             'IPBZ': 'IP BZ'}

def get_invalid_pilot_quals(pilots, quals_map=quals_map):
    invalid_quals = {}
    for p in pilots.keys():
        for month in pilots[p]['Quals'].keys():
            if pilots[p]['Quals'][month]:
                qual = pilots[p]['Quals'][month]
                if qual in quals_map.keys():
                    invalid_quals[p] = pilots[p]  
    return invalid_quals

def clean_pilot_quals(pilots, quals_map=quals_map):
    for p in pilots.keys():
        for month in pilots[p]['Quals'].keys():
            if pilots[p]['Quals'][month]:
                qual = pilots[p]['Quals'][month]
                if qual in quals_map.keys():
                    pilots[p]['Quals'][month] = quals_map[qual]
    return pilots
