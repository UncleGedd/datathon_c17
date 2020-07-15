import seaborn as sns
import pandas as pd
from DataLoader import *


def pilotLeave(staff_list):
    # Plots staff leave as a heatmap (x axis - days, y axis - staff id)
    # Staff list - list of staff members by id that you want to include in the chart
    STAFF = loadPilotData()

    # Find min and Max dates
    min_day = 99999999
    max_day = -1
    for staff_id in staff_list:
        staff_member = STAFF[staff_id]
        leave_intervals = staff_member['Leave']
        for interval in leave_intervals:
            start = int(interval[0])
            end = int(interval[1])

            min_day = int(min(min_day, start))
            max_day = int(max(max_day, end))

    # Initialize Empty Dict of Leave
    leave_dict = {}
    for day in range(min_day, max_day+1):
        for staff_id in staff_list:
            leave_dict[(staff_id, day)] = 0

    # Fill in Leave
    for staff_id in staff_list:
        staff_member = STAFF[staff_id]
        leave_intervals = staff_member['Leave']
        for interval in leave_intervals:
            start = int(interval[0])
            end = int(interval[1])
            for day in range(start, end + 1):
                leave_dict[(staff_id, day)] = 1

    leave_data = []
    for leave_info, leave_val in leave_dict.items():
        staff_id = leave_info[0]
        day = leave_info[1]
        leave_data.append([staff_id, day, leave_val])

    # Massage into DataFrame
    column_names = ['Staff_ID', 'Day', 'Leave']
    df = pd.DataFrame(leave_data, columns=column_names)
    leave = df.pivot('Staff_ID', 'Day', 'Leave')
    ax = sns.heatmap(leave, cmap="RdBu_r", cbar=False)
    ax.tick_params(axis='both', which='both', length=0)


def eventCalendar(event_list):
    # Plots events as a heatmap (x axis - days, y axis - event id)
    # Event list - list of staff members by id that you want to include in the chart
    EVENTS = loadEventData()


    # Find min and Max dates
    min_day = 99999999
    max_day = -1
    for event_id in event_list:
        event = EVENTS[event_id]
        start = event['StartDay']
        end = event['EndDay']

        min_day = int(min(min_day, start))
        max_day = int(max(max_day, end))

    # Initialize Empty Dict of missions
    event_dict = {}
    for day in range(min_day, max_day+1):
        for event_id in event_list:
            event_dict[(event_id, day)] = 0

    # Fill in Events
    for event_id in event_list:
        event = EVENTS[event_id]
        start = int(event['StartDay'])
        end = int(event['EndDay'])
        for day in range(start, end + 1):
            event_dict[(event_id, day)] = 1

    event_data = []
    for event_info, event_val in event_dict.items():
        staff_id = event_info[0]
        day = event_info[1]
        event_data.append([staff_id, day, event_val])

    # Massage into DataFrame
    column_names = ['Event_ID', 'Day', 'Scheduled']
    df = pd.DataFrame(event_data, columns=column_names)
    leave = df.pivot('Event_ID', 'Day', 'Scheduled')
    ax = sns.heatmap(leave, cmap="RdBu_r", cbar=False)
    ax.tick_params(axis='both', which='both', length=0)