import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_daily_wip(log, wip_time='15:00:00'):
    data = log.data
    
    # Create unduplicated list of all days at the desired count time
    all_days = pd.to_datetime(data['StartTimeStamp'].dt.date.astype(str) + ' ' + wip_time).drop_duplicates()
    all_days = all_days.sort_values()

    # Count WIP for all eventlog days at the set WIP time - ideally end-of-day
    rows = []
    for day in all_days:
        count_wip = ((data['StartTimeStamp'] < day) & (data['EndTimeStamp'] > day)).sum()
        rows.append({'day': day, 'total_wip': count_wip})

    wip_output = pd.DataFrame(rows)

    # Plot the outcome
    plt.figure(figsize=(8, 5))
    plt.bar(wip_output['day'], wip_output['total_wip'], color='skyblue')
    plt.xlabel("Day")
    plt.ylabel('Total WIP')
    plt.title('Total WIP per Day')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()

    # Show plot
    plt.show()







def plot_utilisation(log, AHT_min_column='A-AHT\n (min)', AVAILABLE_WORK_HOURS_PER_FTE_PER_WEEK=30, TOTAL_FTE=60):
    """
    
    
    make sure you have a "AHT" column in log.activity_log
    """

    # Merge AHT data from activity log with main log
    data_2 = pd.merge(log.data, log.activity_log[['Activity', AHT_min_column]], on='Activity', how='left')

    # Create a week number column
    data_2['EndStamp WeekNum'] = data_2['EndTimeStamp'].dt.isocalendar().week

    # Create a pivot table based on Week Numbers (ps: this is based on ISO and different than Excel default)
    productivity_table = data_2.pivot_table(values=['Activity', AHT_min_column], index='EndStamp WeekNum',
                                           aggfunc={'Activity': 'count', AHT_min_column: 'sum'})

    # Calculate the FTEs worth of work & FTE Utilisation
   
    productivity_table['Equivalent FTEs of work'] = productivity_table[AHT_min_column] / (60 * AVAILABLE_WORK_HOURS_PER_FTE_PER_WEEK )
    productivity_table['Utilisation'] = productivity_table[AHT_min_column] / (60 * AVAILABLE_WORK_HOURS_PER_FTE_PER_WEEK * TOTAL_FTE)
    productivity_table = productivity_table.reset_index()
    log.utilisation = productivity_table

    # Plot weekly Utilisation
    fig, ax = plt.subplots(figsize=(16, 6))
    productivity_table.plot(x= 'EndStamp WeekNum', y = 'Utilisation', kind= 'bar', legend=False, ax=ax, width=0.9 )
    # ax.set_xlim([1,5])
    ax.set_ylim([0, 1])
    plt.xlabel('Week Number')
    plt.ylabel('Utilisation')
    plt.title('Weekly Utilisation')

    # Show the plot
    plt.show()


