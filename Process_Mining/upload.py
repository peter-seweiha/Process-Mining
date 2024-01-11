import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.cm import get_cmap
from matplotlib.colors import to_rgba
import matplotlib.dates as mdates

import math

from datetime import date
from IPython.display import Markdown, display



class upload:
    def __init__(self, input_log):
        if not isinstance(input_log, pd.DataFrame):
            raise ValueError("EventLog must be a pandas DataFrame.")
        self.data = input_log
        
    def clean_log(self, CaseID='caseid_column', Activity='activity_column', StartTimeStamp='start_column', EndTimeStamp='end_column', Role= 'role_column', Resource = 'resource_column'):
        
        # create a dictionary to map old column names to new column names
        rename_dict = {CaseID: 'CaseID', Activity: 'Activity', StartTimeStamp: 'StartTimeStamp', EndTimeStamp: 'EndTimeStamp' , Role: 'Role', Resource: 'Resource' }
        
        # use the rename method to rename the columns in the DataFrame
        self.data = self.data.rename(columns=rename_dict)
       
        # fix columns data types in Python
        # Convert CaseID column to string
        self.data['CaseID'] = self.data['CaseID'].astype(str)
        
        # convert datetime column and set the correct format (dd-mm)
        self.data['StartTimeStamp'] = pd.to_datetime(self.data['StartTimeStamp'], dayfirst=True)
        self.data['EndTimeStamp'] = pd.to_datetime(self.data['EndTimeStamp'], dayfirst=True)



        #__________________________

    def generate_case_log(self, case_attributes=[]):
        # Create a table for case Attributes without duplicates
        case_attributes_table = self.data[case_attributes + ['CaseID']].drop_duplicates(subset=['CaseID'])

        # Create a list of unduplicated Case IDs
        case_ids = self.data['CaseID'].drop_duplicates().tolist()

        # Initialize list to store case logs
        rows = []

        # Loop to create a Case Log
        for case in case_ids:
            case_activities = self.data[self.data['CaseID'] == case]

            # Sort events based on start date & time
            case_activities = case_activities.sort_values(by='StartTimeStamp', ascending=True)

            # Get first timestamp in case
            first_start_stamp = case_activities['StartTimeStamp'].iloc[0]

            # Get last timestamp in case
            last_end_stamp = case_activities['EndTimeStamp'].iloc[-1]

            # Get number of activities per case
            activity_instances = len(case_activities)

            # Write all application journey in one string
            variant = case_activities['Activity'].str.cat(sep='->')
            rows.append({
                'CaseID': case,
                'first_start_stamp': first_start_stamp,
                'last_end_stamp': last_end_stamp,
                'activity_instances': activity_instances,
                'variant': variant
            })

        # Create DataFrame from rows
        case_log = pd.DataFrame(rows)

        # Add case attributes
        case_log = pd.merge(case_log, case_attributes_table, on='CaseID', how='left')

        # Add case duration column
        case_log['case_duration_days'] = (case_log['last_end_stamp'] - case_log['first_start_stamp']).dt.total_seconds() / (60 * 60 * 24)

        # Drop case attributes from main log
        self.data.drop(case_attributes, axis=1, inplace=True)

        # Export the caselog to CSV file for later use
        case_log.to_csv('_case_log.csv', index=False)

        # Save case log to the object for further use if needed
        self.case_log = case_log



    def generate_activity_log(self, activity_attributes=[]):
        # Create a table for case Attributes without duplicates
        activity_attributes_table = self.data[['Activity'] + activity_attributes].drop_duplicates(subset=['Activity'])

        # Create a list of unduplicated Case IDs
        self.activities = self.data['Activity'].drop_duplicates().tolist()

        # Create a dataframe with activity counts
        activity_counts = self.data['Activity'].value_counts().reset_index()
        activity_counts.columns = ['Activity', 'A-count']

        # Merge activity counts and attributes table on 'Activity'
        self.activity_log = pd.merge(activity_counts, activity_attributes_table, on='Activity', how="left")

        # Export the activity log to CSV file for later use
        self.activity_log.to_csv('_activity_log.csv', index=False)

        # Drop activity attributes from the main log
        self.data.drop(activity_attributes, inplace=True)

    def add_case_log_file(self, case_log_df=None):
        # Merge existing case log with external file & drop duplicated columns
        self.case_log = pd.merge(self.case_log, case_log_df, on='CaseID', how="left", suffixes=('', '_y'))
        self.case_log.drop(self.case_log.filter(regex='_y$').columns, axis=1, inplace=True)

        # Export the caselog to CSV file for later use
        self.case_log.to_csv('_case_log.csv', index=False)

        # self.case_log.columns = ['c-' + col if col != 'CaseID' else col for col in self.case_log.columns]

    def add_activity_log_file(self, activity_log_df=None):
        # Merge existing activity log with external file
        self.activity_log = pd.merge(self.activity_log, activity_log_df, on='Activity', how='left', suffixes=('', '_y'))
        self.activity_log.drop(self.activity_log.filter(regex='_y$').columns, axis=1, inplace=True)

        # Export the activity log to CSV file for later use
        self.activity_log.to_csv('_activity_log.csv', index=False)
        
        # self.activity_log.columns = ['A-' + col if col != 'Activity' else col for col in self.activity_log.columns]