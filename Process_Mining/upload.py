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