import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def add_start_event(log):
    data = log.data
    
    app_numbers = data['CaseID'].drop_duplicates().tolist()

    for app in app_numbers:
        app_events = data[data['CaseID']==app]

        #Sort events based on StartTimestamp
        app_events = app_events.sort_values (by='StartTimeStamp', ascending = True)

        # Duplicate first raw to dataset
        row_to_duplicate = app_events.iloc[0]
        data = data.append(row_to_duplicate, ignore_index=True)

        # Get and sort app events again
        app_events = data[data['CaseID']==app]

        #Sort events based on StartTimestamp
        app_events = app_events.sort_values (by='StartTimeStamp', ascending = True)    

        # Replace values in the newly created row
        new_index = app_events.index[0]
        new_activity_name = 'start'
    #     new_role_name = 'start'
        new_end_timestamp = app_events ['StartTimeStamp'].iloc[0]

        data.at[data.index[new_index],'Activity'] = new_activity_name
        data.at[data.index[new_index],'EndTimeStamp'] = new_end_timestamp
    #     data.at[data.index[new_index],'Role'] = new_role_nameevents 

    # Generate AHT table
    # Create a list of undublicated activities in a DataFrame
    AHT_DataEntry = data['Activity'].drop_duplicates().to_frame()

    # Create a column to fill AHT data
    AHT_DataEntry['AHT (min) - please fill']=None
    AHT_DataEntry.to_csv('AHT_DataEntry.csv', index = False)

    print('please fill AHT data in the [AHT_DataEntry.csv] file ')
    
    log.log_with_start_activity = data

    return log.log_with_start_activity
    

def enrich_with_AHT_simple(log, AHT_DataEntry_path = 'AHT_DataEntry.csv'):
    
    """This function will take the log enriched with Start Step in addition to AHT values provided by the user and add AHT for each activity
    Simple means this function will change start time stamp to accommodate the exact AHT provided by the user
    (unless the data duration is lower than the AHT)
    """
    
    data = log.log_with_start_activity
    AHT_DataEntry = pd.read_csv(AHT_DataEntry_path)

    # Add AHT from table to data
    dataset = pd.merge(data, AHT_DataEntry, on='Activity', how='left')

    # Convert AHT to TimeDelta
    dataset['AHT (min) - please fill'] = pd.to_timedelta(dataset['AHT (min) - please fill'], unit="m")

    # Change "StartTimeStamp" to "AssignedTimeStamp"
    dataset.rename(columns={'StartTimeStamp': 'AssignedTimeStamp'}, inplace=True)

    # Create activity duration column
    dataset["activity_duration"] = dataset['EndTimeStamp'] - dataset['AssignedTimeStamp']

    # Generate the new StartTimeStamps
    dataset['StartTimeStamp'] = dataset['EndTimeStamp'] - dataset[['AHT (min) - please fill', 'activity_duration']].min(axis=1)

    # Drop unneeded columns
    dataset = dataset.drop(['AHT (min) - please fill', 'activity_duration'], axis=1)

    log.enriched_log = dataset
    
    return log.enriched_log
