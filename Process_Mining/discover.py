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


def info(log):
        # Provide basic information on dataset
        print('This Event Log has {} rows and {} columns.'.format(log.data.shape[0], log.data.shape[1]))
        print("")
        print("Number of unique Cases in dataset:", len(log.data['CaseID'].drop_duplicates()))
        print("Number of unique Activities in dataset:", len(log.data['Activity'].drop_duplicates()))
        print("")
        print("Minimum number of instances per case:", min(log.data['CaseID'].value_counts()))
        print("Maximum number of instances per case:", max(log.data['CaseID'].value_counts()))
        print("")
        print("Log earliest date:", log.data['StartTimeStamp'].min())
        print("Log latest date:", log.data['EndTimeStamp'].max())
    
    
def heatmap(log):
    # Visualize which activities are common to cases
    heat_map = pd.crosstab(log.data['CaseID'], log.data['Activity'])
    heat_map = heat_map.applymap(lambda x: 1 if x else 0)

    nunique = heat_map.apply(pd.Series.nunique)
    shared_actions = nunique[nunique == 1].index
    print("**The following actions are common to all cases**: {}".format(', '.join(shared_actions)))

    plt.figure(figsize=(15, 6))
    sns.heatmap(heat_map, cmap="YlGnBu")
    plt.title("Heatmap showing common activities across all cases")
    plt.show()
    
    
def dotted_chart(log):
    # This function is to provide basic information & visualize the dataset
    
        # Create a pivot table of the start (minimum) and end (maximum) timestamps associated with each case:
    case_starts_ends = log.data.pivot_table(index='CaseID', aggfunc={'StartTimeStamp': ['min'],'EndTimeStamp': ['max'] })
    case_starts_ends = case_starts_ends.reset_index() 
    case_starts_ends.columns = ['CaseID', 'CaseEnd', 'CaseStart'] 

    # Merge with the main event log data so that for each row we have the start and end times.
    graph_data = log.data.merge(case_starts_ends, on='CaseID') 

    # Calculate the relative time by subtracting the process start time from the event timestamp
    graph_data['RelativeTime'] = graph_data['StartTimeStamp'] - graph_data['CaseStart']

    # Calculate case length
    graph_data['CaseLength'] = graph_data['CaseEnd'] - graph_data['CaseStart']

    # Convert relative times to more friendly measures (days)
    graph_data['RelativeTime_days'] = graph_data['RelativeTime'].dt.total_seconds() / 86400

    ## Visualise a dotted chart over time
    plt.figure(figsize=(15, 6))
    ax = sns.scatterplot(x=graph_data['StartTimeStamp'], y=graph_data['CaseID'], hue=graph_data['Activity'])
    plt.title('Dotted chart showing the event flow over absolute time')
    plt.show()

    ## Dotted chart Order by the case length
    ordered = graph_data.sort_values(by=['CaseLength', 'CaseID', 'RelativeTime_days'])

    plt.figure(figsize=(15, 8))
    ax = sns.scatterplot(x=ordered['RelativeTime_days'], y=ordered['CaseID'], hue=ordered['Activity']) 
    plt.title('Dotted chart ordered by case length')
    plt.show()
    
def plot_activity_duration(log):
    
    data = log.data
    
    # Create duration column in dataset
    data['duration'] = data['EndTimeStamp']- data['StartTimeStamp']
    data['duration_day'] = data['duration'].dt.total_seconds() / (60*60*24)  

    # Create a list of unique activities
    activity_list = data['Activity'].drop_duplicates().tolist()

    # get some key parameters
    max_value = data['duration_day'].max()

    # number of histograms per raws & columns
    # import math
    nrows = math.ceil(len(activity_list)/3)
    ncols = 3

    fig, axs = plt.subplots(nrows, ncols, figsize=(12, nrows * 2.5))

    # Flattening the axs array to iterate through it
    axs = axs.flatten()

    # iterate through data to create histograms
    for i in range(len(activity_list)):

        hist_data = data['duration_day'][data['Activity']== activity_list[i]]

        axs[i].hist(hist_data, bins=20, alpha=0.7)
        axs[i].set_title(f'{activity_list[i]}')
        axs[i].set_xlabel('Days')  # Set x-label for each subplot
        axs[i].set_xlim(0, max_value)  # Set dynamic x-axis limits

        # Add subtitle
        axs[i].text(0.5, 0.90, f' count: {len(hist_data)} - mean: {round(hist_data.mean(),1)}', fontsize=8, ha='center', transform=axs[i].transAxes)

        # Hiding empty subplots if any
        for j in range(len(activity_list), len(axs)):
            axs[j].axis('off')

    # Adding a title for the entire figure
    plt.suptitle('Activities Durations and Distribution', fontsize=16, fontweight='bold')

    # Adjust layout and display the figure
    plt.tight_layout()
    plt.show()
    
    
def case_timeline (log, CaseID = '52', coloring_variable = 'Activity' ):
    """
    this function draws a bar diagram showing a one case timeline and 
    you can change the bar colors accroding to any variable available in dataset
    """
    # from matplotlib.cm import get_cmap
    # from matplotlib.colors import to_rgba
    # import matplotlib.dates as mdates

    case_analysis = log.data[log.data['CaseID']==CaseID]

    repeat_activities = pd.DataFrame(case_analysis['Activity'].value_counts())
    print('the following Activities are repeated more than once in this case : ')
    print (repeat_activities[repeat_activities['Activity']>1])

    # This is the key line and needs to be fixed to get the graph in order
    grouped_case_analysis = case_analysis.groupby('Activity')
    grouped_case_analysis = sorted(grouped_case_analysis, key=lambda x: x[1]['StartTimeStamp'].min())

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(18, 6))

    # Get a categorical color map
    cmap = get_cmap('tab10')

    # Create a mapping between unique 'Coloring_variable' values and colors
    role_colors = {role: cmap(i) for i, role in enumerate(case_analysis[coloring_variable].unique())}

    # Plot broken bars for each activity with different colors
    for i, (activity, group) in enumerate(grouped_case_analysis):
        for index, row in group.iterrows():
            start_date = row['StartTimeStamp']
            end_date = row['EndTimeStamp']
            duration = (end_date - start_date).total_seconds() / (60 * 60 * 24)  # Convert seconds to days
            color = role_colors[row[coloring_variable]]
            ax.broken_barh([(start_date, duration)], (i - 0.4, 0.8), facecolors=color, edgecolor='black', alpha=0.7)

    # Create a legend
    legend_labels = [role for role in case_analysis[coloring_variable].unique()]
    legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=role_colors[role], markersize=10) for role in legend_labels]
    ax.legend(legend_handles, legend_labels, title=coloring_variable, loc='lower right')

    # Customize the plot
    ax.set_yticks(range(len(grouped_case_analysis)))
    ax.set_yticklabels([activity for activity, _ in grouped_case_analysis])
    ax.set_xlabel('Timeline')
    ax.set_title('Activity Timeline')

    # Step 7: Customize the chart
    ax.xaxis_date()
    # ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    plt.grid(True)
    # Display the plot
    plt.show()