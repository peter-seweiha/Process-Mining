import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def filter_cases_by_activity(log, activities_list=['New Case', 'General Enquiries'], action='retain', matching='any value'):
        
        if (action == 'retain') and (matching == 'any value'):
            print(f'Retain cases that contain any of the following activities ({activities_list})')
            relevant_caseids = log.case_log[log.case_log['variant'].str.contains('|'.join(activities_list))][["CaseID"]]
        
        if (action == 'retain') and (matching == 'all values'):
            print(f'Retain cases that contain all the following activities ({activities_list})')
            relevant_caseids = log.case_log[log.case_log['variant'].str.contains('&'.join(activities_list))][['CaseID']]
        
        if (action == 'remove') and (matching == 'any value'):
            print(f'Remove cases that contain any of the following activities ({activities_list})')
            relevant_caseids = log.case_log[~log.case_log['variant'].str.contains('|'.join(activities_list))][['CaseID']]
        
        if (action == 'remove') and (matching == 'all values'):
            print(f'Remove cases that contain all the following activities ({activities_list})')
            relevant_caseids = log.case_log[~log.case_log['variant'].str.contains('&'.join(activities_list))][['CaseID']]

        filtered_log = log.data[log.data['CaseID'].isin(relevant_caseids['CaseID'])]
        return filtered_log