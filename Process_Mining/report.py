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