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


def filter_events_between(log, retain=True, from_activity='abd', from_first_occurrence=True, from_included=False, to_activity='abc', to_first_occurrence=False, to_included=False):
    # print the filter text to explain the filtering process
    retain_txt = ''
    from_occ_txt = ''
    from_incl_txt = ''
    to_occ_txt = ''
    to_incl_txt = ''
    
    if retain == True:
        retain_txt = 'Retain all activities between ('
    else:
        retain_txt = 'Remove all activities between ('

    if from_activity == '':
        from_occ_txt = ' case start) and '
    else:
        if from_first_occurrence == True:
            from_occ_txt = f'the first occurrence of activity [{from_activity}]'
        else:
            from_occ_txt = f'the last occurrence of activity [{from_activity}]'
        if from_included == True:
            from_incl_txt = ', activity included) and '
        else:
            from_incl_txt = ', activity not included) and '
    
    if to_activity == '':
        to_occ_txt = ' (case end).'
    else:
        if to_first_occurrence == True:
            to_occ_txt = f'the first occurrence of activity [{to_activity}]'
        else:
            to_occ_txt = f'the last occurrence of activity [{to_activity}]'
        if to_included == True:
            to_incl_txt = ', activity included).'
        else:
            to_incl_txt = ', activity not included).'

    print(retain_txt + from_occ_txt + from_incl_txt + to_occ_txt + to_incl_txt)
    
    # the code for the filter
    case_list = filtered_case_log['CaseID'].drop_duplicates().tolist()
    
    for case in case_list:
        # create an empty dataframe to store the output log
        filtered_log = pd.DataFrame()
        
        # isolate activities case by case
        case_activities = log.data[log.data['CaseID'] == case]
        
        # Sort events based on start date & time
        case_activities = case_activities.sort_values(by='StartTimeStamp', ascending=True)
        
        # re-index the isolated case log
        case_activities_reindx = case_activities.reset_index(drop=True)
        
        # calculate from parameters
        if from_activity == '':
            from_indx = None
        elif (from_first_occurrence == True) & (from_included == False):
            from_indx = (case_activities_reindx[case_activities_reindx['Activity'] == from_activity].index.min() + 1)
        elif (from_first_occurrence == True) & (from_included == True):
            from_indx = (case_activities_reindx[case_activities_reindx['Activity'] == from_activity].index.min())
        elif (from_first_occurrence == False) & (from_included == False):
            from_indx = (case_activities_reindx[case_activities_reindx['Activity'] == from_activity].index.max() + 1)
        elif (from_first_occurrence == False) & (from_included == True):
            from_indx = (case_activities_reindx[case_activities_reindx['Activity'] == from_activity].index.max())
        
        # calculate "to" parameters
        if to_activity == '':
            to_indx = None
        elif (to_first_occurrence == True) & (to_included == False):
            to_indx = (case_activities_reindx[case_activities_reindx['Activity'] == to_activity].index.min())
        elif (to_first_occurrence == True) & (to_included == True):
            to_indx = (case_activities_reindx[case_activities_reindx['Activity'] == to_activity].index.min() + 1)
        elif (to_first_occurrence == False) & (to_included == False):
            to_indx = (case_activities_reindx[case_activities_reindx['Activity'] == to_activity].index.max())
        elif (to_first_occurrence == False) & (to_included == True):
            to_indx = (case_activities_reindx[case_activities_reindx['Activity'] == to_activity].index.max() + 1)
        
        # calculate the retain part and append the case to output filtered log
        if retain == True:
            df_to_append = case_activities_reindx.iloc[from_indx:to_indx]
            filtered_log = filtered_log.append(df_to_append)
        
        if retain == False:
            df_to_append = case_activities_reindx[~case_activities_reindx.isin(case_activities_reindx.iloc[from_indx:to_indx])].dropna()
            filtered_log = filtered_log.append(df_to_append)
    
    return filtered_log
