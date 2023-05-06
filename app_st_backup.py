import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pymongo
import streamlit as st
from datetime import datetime, timedelta, time
import altair as alt
import seaborn as sns


def get_start_sleep_time(df):

    # Convert 'dateTime' column to datetime objects
    df.loc[:, 'dateTime'] = pd.to_datetime(df['data'].apply(lambda x: x['dateTime']))

    # Set 'dateTime' as the index of the DataFrame
    df.set_index('dateTime', inplace=True)

    # Extract the hour from the "value" key and store it in a new column
    df['hour'] = pd.to_datetime(df['data'].apply(lambda x: x['value'])).dt.strftime('%H:%M')

    # Drop the 'data' and 'type' columns
    df.drop(['data', 'type'], axis=1, inplace=True)

    # Convert 'hour' column to datetime objects
    df['hour'] = pd.to_datetime(df['hour'], format='%H:%M').dt.time

    # Calculate new_hour based on conditions (if hour > 12:00 then hour -12:00 else if hour < 12:00 then hour + 12:00
    # We do this to sort the hours accordingly, e.g. 23:30 is earlier than 00:25 and 05:23 is later than 00:25
    df['new_hour'] = df.apply(lambda row: (datetime.combine(datetime.min, row['hour']) - timedelta(hours=12)).time() if row['hour'] >= time(hour=12)
                              else (datetime.combine(datetime.min, row['hour']) + timedelta(hours=12)).time(), axis=1)

    # Convert new_hour to string format
    df['new_hour'] = df['new_hour'].apply(lambda x: x.strftime('%H:%M'))

    # Sort the DataFrame by the 'new_hour' column
    df.sort_values(by='new_hour', inplace=True)
    return df


def get_data_value_minutes(df):

    # Convert 'dateTime' column to datetime objects
    df.loc[:, 'dateTime'] = pd.to_datetime(df['data'].apply(lambda x: x['dateTime']))
    # Set 'dateTime' as the index of the DataFrame
    df.set_index('dateTime', inplace=True)
    # Extract value from data - value
    df.loc[:, 'value'] = df['data'].apply(lambda x: x['value'])
    # Drop the 'data' and 'type' columns
    df.drop(['data', 'type'], axis=1, inplace=True)

    df['value'] = df['value'].astype(int)
    # Calculate hours and minutes
    df['hours'] = df['value'] // 60
    df['minutes'] = df['value'] % 60
    df['hours'] = df['hours'].apply(lambda x: '{:02d}h'.format(x))
    df['minutes'] = df['minutes'].apply(lambda x: '{:02d}m'.format(x))
    df['hours_minutes'] = df['hours'] + ' ' + df['minutes']

    # Drop the 'hours' and 'minutes' columns
    df.drop(['hours', 'minutes'], axis=1, inplace=True)

    # Sort the DataFrame by the 'new_hour' column
    df.sort_values(by='hours_minutes', inplace=True)
    return df


def get_steps_value(df):
    # Convert 'dateTime' column to datetime objects
    df.loc[:, 'dateTime'] = pd.to_datetime(df['data'].apply(lambda x: x['dateTime']))

    # Extract 'score' from 'value' column
    df.loc[:, 'steps'] = df['data'].apply(lambda x: x['value'])

    # Drop the 'data' and 'type' columns
    df.drop(['data', 'type'], axis=1, inplace=True)

    # Sort the DataFrame by the 'dateTime' column
    df.sort_values(by='dateTime', ascending=True, inplace=True)

    df.set_index('dateTime', inplace=True)

    # Convert the 'steps' column to a numeric data type
    df['steps'] = df['steps'].astype('int')

    # Sort the DataFrame by the 'dateTime' column
    df = df.sort_values(by='dateTime')
    
    #Make an extra column with the activity level
    df=df.assign(activity_level = 'normal_activity')

    for index, row in df.iterrows():
        if row['steps'] > 10000:
            df.at[index, 'activity_level'] = 'high_activity'
        elif row['steps'] < 500 and row['steps'] != 0:
            df.at[index, 'activity_level'] = 'low_activity'
        elif row['steps'] == 0:
            df.at[index, 'activity_level'] = 'not_wearing_it'
    
    return df

def streamlit_sleep_layout():
    # setting the screen size
    st.set_page_config(layout="wide", page_title="Fitbit Data")
    # main title
    st.title('Fitbit Sleep MongoDB')
    # main text
    st.subheader('This app is a Streamlit app that retrieve mongodb data and show it in a dataframe')


def streamlit_start_sleep_chart(df,  y_label, title):

    fig = plt.figure(figsize=(12, 5))

    df = df.sort_values('new_hour') # sort the DataFrame by new_hour column

    plt.bar(df.index, df['new_hour'])

    plt.xlabel('Date')
    plt.xticks(df.index, df.index.strftime('%Y-%m-%d'), rotation=90, ha='center')

    plt.ylabel(y_label)
    plt.yticks(df['new_hour'], df['hour'])

    plt.title(title)

    plt.tight_layout()
    st.pyplot(fig)


def streamlit_sleep_charts(df, y_label, title):

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.bar(df.index, df['hours_minutes'])

    ax.set_xlabel('Date')
    plt.xticks(df.index, df.index.strftime('%Y-%m-%d'), rotation=90)

    ax.set_ylabel(y_label)
    ax.set_yticklabels(df['hours_minutes'].values)

    ax.set_title(title)

    plt.tight_layout()
    st.pyplot(fig)


def minutes_in_hours_minutes(df):
    # Convert 'dateTime' column to datetime objects
    df.loc[:, 'dateTime'] = pd.to_datetime(df['data'].apply(lambda x: x['dateTime']))
    # Set 'dateTime' as the index of the DataFrame
    df.set_index('dateTime', inplace=True)
    # Extract value from data - value
    df.loc[:, 'value'] = df['data'].apply(lambda x: x['value'])
    # Drop the 'data' and 'type' columns
    df.drop(['data', 'type'], axis=1, inplace=True)
    df['value'] = df['value'].astype(int)

    new_df = pd.DataFrame(index=df.index, columns=df.columns)
    new_df = df.applymap(lambda x: x // 60 + (x % 60) / 100)
    new_col = new_df['value']
    return new_col


def streamlit_sleep_stages_chart(duration, deep_sleep, light_sleep, rem_sleep, awake_sleep):
    # sort the dates
    duration = duration.sort_index()
    light_sleep = light_sleep.sort_index()
    deep_sleep = deep_sleep.sort_index()
    rem_sleep = rem_sleep.sort_index()
    awake_sleep = awake_sleep.sort_index()

    # get the dates for the x-axis
    dates = duration.index.strftime('%Y-%m-%d')

    # set the width of the bars
    bar_width = 0.15

    # set the positions of the bars on the x-axis
    r1 = np.arange(len(duration))
    r2 = [x + bar_width for x in r1]
    r3 = [x + bar_width for x in r2]
    r4 = [x + bar_width for x in r3]
    r5 = [x + bar_width for x in r4]

    # create the plot
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(r1, duration, width=bar_width, label='Sleep duration')
    ax.bar(r2, light_sleep, width=bar_width, label='Light Sleep')
    ax.bar(r3, deep_sleep, width=bar_width, label='Deep Sleep')
    ax.bar(r4, rem_sleep, width=bar_width, label='REM Sleep')
    ax.bar(r5, awake_sleep, width=bar_width, label='Wake Sleep')

    # add x-axis ticks and labels
    ax.set_xticks(r2)
    ax.set_xticklabels(dates, rotation=90)
    ax.set_xlabel('Date')

    # add y-axis label
    ax.set_ylabel('Hours')

    # add chart title
    ax.set_title('Sleep Data')

    # add legend
    ax.legend()

    # show the plot
    plt.tight_layout()
    st.pyplot(fig)

def streamlit_steps(df):
    # Create a figure and axis object
    fig, ax = plt.subplots(figsize=(12, 5))

    # Create a scatter plot with the DataFrame
    ax.scatter(df.index, df['steps'], color='b')
    for dateTime, row in df.iterrows():
        ax.text(dateTime, row['steps'], str(int(row['steps'])), ha='center', va='bottom', fontdict={'size': 9})

    ax.axhline(y=10000, color='green', linestyle='--', alpha=0.5)
    ax.axhline(y=500, color='magenta', linestyle='--', alpha=0.5)

    # Create a line plot with the same x-axis values and the 'steps' column of the DataFrame
    ax.plot(df.index, df['steps'], color='r')

    # Set the x-axis tick locations and labels
    tick_labels = df.index.strftime('%Y-%m-%d')
    ax.set_xticks(df.index)
    ax.set_xticklabels(tick_labels, rotation=90)

    # Set the y-axis tick locations and labels
    ax.set_yticks(
        np.arange(df['steps'].min(), df['steps'].max() + 10000, 1000))  # Set y-axis ticks to a range of values
    ax.set_ylim(df['steps'].min(), df['steps'].max() + 1500)  # Set y-axis limits to a range of values

    # Set the x-axis label
    ax.set_xlabel('Date')

    # Set the y-axis label
    ax.set_ylabel('Steps')

    # Set the title
    ax.set_title('Steps per Day')


    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
    plt.tight_layout()
    # Show plot in Streamlit
    st.pyplot(fig)

def streamlit_steps_pie(df):
    # count the number of occurrences of each value in the activity_level column
    value_counts = df['activity_level'].value_counts(normalize=True)

    # create a pie chart using Matplotlib
    fig, ax = plt.subplots()
    ax.pie(
        value_counts.values,
        labels=value_counts.index,
        autopct='%1.1f%%',
        colors=['purple', 'green', 'blue', 'gray'],
        startangle=90
    )

    # set the title of the chart
    ax.set_title('Percentage of activity level based on the number of steps')

    # adjust the size of the plot
    fig.set_size_inches(6, 6)

    # adjust the resolution of the plot
    fig.set_dpi(200)

    # adjust the aspect ratio of the plot to make it less zoomed in
    ax.set_box_aspect(0.4)

    # display the chart in the Streamlit app
    plt.tight_layout()
    st.pyplot(fig)

def get_data_value(df):
    # Convert 'dateTime' column to datetime objects
    df.loc[:, 'dateTime'] = pd.to_datetime(df['data'].apply(lambda x: x['dateTime']))
    # Set 'dateTime' as the index of the DataFrame
    df.set_index('dateTime', inplace=True)
    # Extract value from data - value
    df.loc[:, 'value'] = df['data'].apply(lambda x: x['value'])
    df.loc[:, 'dateTime'] = df['data'].apply(lambda x: x['dateTime'])
    df.drop(['data', 'type'], axis=1, inplace=True)
    # Drop the 'data' and 'type' columns
    return df

def get_user_engagement(totalWearTime_df, duration_df):
    print(totalWearTime_df)
    # # Convert 'dateTime' column to datetime objects
    # totalWearTime_df.loc[:, 'dateTime'] = pd.to_datetime(totalWearTime_df['data'].apply(lambda x: x['dateTime']))
    # # Set 'dateTime' as the index of the DataFrame
    # totalWearTime_df.set_index('dateTime', inplace=True)
    # # Extract value from data - value
    # totalWearTime_df.loc[:, 'value'] = totalWearTime_df['data'].apply(lambda x: x['value'])
    # totalWearTime_df.loc[:, 'dateTime'] = totalWearTime_df['data'].apply(lambda x: x['dateTime'])
    # # Drop the 'data' and 'type' columns
    # totalWearTime_df.drop(['data', 'type'], axis=1, inplace=True)

    new_totalWearTime_df = get_data_value(totalWearTime_df)
    new_totalWearTime_df['total_wear_time'] = round(new_totalWearTime_df['value'] / 60, 2)
    
    new_duration_df = duration_df.applymap(lambda x: x // 60 + (x % 60) / 100)

    merged_df = pd.merge(new_totalWearTime_df, new_duration_df, left_index=True, right_index=True, how='outer')
    merged_df.drop(['value_x'], axis=1, inplace=True)
    merged_df = merged_df.rename(columns={'value_y': 'sleep_duration'})

    # Display plot in Streamlit app
    plt.rcParams['font.size'] = 3

    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    merged_df.plot.bar(x = 'dateTime', y=['total_wear_time','sleep_duration'],ax=ax)
    st.pyplot(fig)

def get_user_activity(df2):
    minutesSedentary_df = df2[df2['type']=='minutesSedentary']
    minutesLightlyActive_df = df2[df2['type']=='minutesLightlyActive']
    minutesFairlyActive_df = df2[df2['type']=='minutesFairlyActive']
    minutesVeryActive_df = df2[df2['type']=='minutesVeryActive']

    new_minutesSedentary_df = get_data_value(minutesSedentary_df)
    new_minutesLightlyActive_df = get_data_value(minutesLightlyActive_df)
    new_minutesFairlyActive_df = get_data_value(minutesFairlyActive_df)
    new_minutesVeryActive_df = get_data_value(minutesVeryActive_df)

    new_minutesSedentary_df['minutesSedentary'] = round(new_minutesSedentary_df['value'] / 60, 2)
    new_minutesLightlyActive_df['minutesLightlyActive'] = round(new_minutesLightlyActive_df['value'] / 60, 2)
    new_minutesFairlyActive_df['minutesFairlyActive'] = round(new_minutesFairlyActive_df['value'] / 60, 2)
    new_minutesVeryActive_df['minutesVeryActive'] = round(new_minutesVeryActive_df['value'] / 60, 2)

    new_minutesSedentary_df.drop(['dateTime','value'], axis=1, inplace=True)
    new_minutesLightlyActive_df.drop(['dateTime','value'], axis=1, inplace=True)
    new_minutesFairlyActive_df.drop(['dateTime','value'], axis=1, inplace=True)
    new_minutesVeryActive_df.drop(['dateTime','value'], axis=1, inplace=True)
    
    # Calculate total time spent in each activity level
    sedentary_time = new_minutesSedentary_df.sum()['minutesSedentary']
    lightly_active_time = new_minutesLightlyActive_df.sum()['minutesLightlyActive']
    fairly_active_time = new_minutesFairlyActive_df.sum()['minutesFairlyActive']
    very_active_time = new_minutesVeryActive_df.sum()['minutesVeryActive']

    # Create pie chart
    labels = ['Very','Sedentary', 'Fairly', 'Lightly']
    sizes = [very_active_time, sedentary_time, fairly_active_time, lightly_active_time]
    plt.rcParams['font.size'] = 4

    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    ax.set_title('Percentage of Time Spent in Each Activity Level')
    st.pyplot(fig)

def get_activity_per_day(df2):
    minutesSedentary_df = df2[df2['type']=='minutesSedentary']
    minutesLightlyActive_df = df2[df2['type']=='minutesLightlyActive']
    minutesFairlyActive_df = df2[df2['type']=='minutesFairlyActive']
    minutesVeryActive_df = df2[df2['type']=='minutesVeryActive']

    new_minutesSedentary_df = get_data_value(minutesSedentary_df)
    new_minutesLightlyActive_df = get_data_value(minutesLightlyActive_df)
    new_minutesFairlyActive_df = get_data_value(minutesFairlyActive_df)
    new_minutesVeryActive_df = get_data_value(minutesVeryActive_df)

    new_minutesSedentary_df['minutesSedentary'] = round(new_minutesSedentary_df['value'] / 60, 2)
    new_minutesLightlyActive_df['minutesLightlyActive'] = round(new_minutesLightlyActive_df['value'] / 60, 2)
    new_minutesFairlyActive_df['minutesFairlyActive'] = round(new_minutesFairlyActive_df['value'] / 60, 2)
    new_minutesVeryActive_df['minutesVeryActive'] = round(new_minutesVeryActive_df['value'] / 60, 2)

    new_minutesSedentary_df.drop(['value'], axis=1, inplace=True)
    new_minutesLightlyActive_df.drop(['dateTime','value'], axis=1, inplace=True)
    new_minutesFairlyActive_df.drop(['dateTime','value'], axis=1, inplace=True)
    new_minutesVeryActive_df.drop(['dateTime','value'], axis=1, inplace=True)

    merged_df = pd.merge(new_minutesSedentary_df, new_minutesLightlyActive_df, left_index=True, right_index=True, how='outer')
    #merged_df.drop(['value_x','dateTime_x','value_y'], axis=1, inplace=True)

    merged_df1 = pd.merge(merged_df, new_minutesFairlyActive_df, left_index=True, right_index=True, how='outer')
    #merged_df1.drop(['dateTime_y','value'], axis=1, inplace=True)

    merged_df2 = pd.merge(merged_df1, new_minutesVeryActive_df, left_index=True, right_index=True, how='outer')
    #merged_df2.drop(['dateTime_x','value'], axis=1, inplace=True)
    merged_df2 = merged_df2.rename(columns={'dateTime_y': 'dateTime'})

    # Create stacked bar chart
    plt.rcParams['font.size'] = 4
    merged_df2 = merged_df2.drop('dateTime', axis=1).reset_index()

    merged_df2['dateTime'] = pd.to_datetime(merged_df2['dateTime'])

    # Melt dataframe to long format
    df_melted = pd.melt(merged_df2, id_vars='dateTime', var_name='activity_type', value_name='minutes')

    # Create stacked bar chart using Altair
    chart = alt.Chart(df_melted).mark_bar().encode(
        x='dateTime:T',
        y='minutes:Q',
        color='activity_type:N'
    ).properties(
        width=400,
        height=800,
        title='Breakdown of Activity Types by Day'
    ).configure_legend(
        orient='top'
    )

    # Show chart using Streamlit
    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":

    # Connect to MongoDB
    client = pymongo.MongoClient()
    db = client.fitbitDB
    collection = db.fitbitCollection

    # save the documents in a dataframe
    df = pd.DataFrame(list(collection.find()))
    # drop the _id and id fields, not needed
    df1 = df.drop(['_id'], axis=1)
    df2 = df1.drop(['id'], axis=1)

    streamlit_sleep_layout()

    # sleep duration
    sleep_duration = df2[df2['type'] == 'timeInBed']
    duration = minutes_in_hours_minutes(sleep_duration)

    # Display the selected chart in an expander
    chart_options = ['Sleep', 'User Engagement']
    selected_chart = st.sidebar.selectbox('Select a chart', chart_options)

    # Display the selected chart
    if selected_chart == 'Sleep':
        # start time
        startTime_df = df2[df2['type'] == 'sleep_startTime']
        startTime_df = get_start_sleep_time(startTime_df)
        streamlit_start_sleep_chart(startTime_df, 'Time (HH:MM)', 'Sleep Start time')
        # timeInBed, minutesAsleep, minutesAwake
        types = ['timeInBed', 'minutesAsleep', 'minutesAwake']
        titles = ['Total Time in bed', 'Total minutes asleep', 'Total minutes awake']
        for idx, x in enumerate(types):
            df = pd.DataFrame()
            df = df2[df2['type'] == x]
            df = get_data_value_minutes(df)
            streamlit_sleep_charts(df,  'Time (hh mm)', titles[idx])

        # deep sleep
        sleep_Deep = df2[df2['type'] == 'sleep_Deep']
        deep_sleep = minutes_in_hours_minutes(sleep_Deep)

        # light sleep
        sleep_Light = df2[df2['type'] == 'sleep_Light']
        light_sleep = minutes_in_hours_minutes(sleep_Light)

        # rem sleep
        sleep_Rem = df2[df2['type'] == 'sleep_Rem']
        rem_sleep = minutes_in_hours_minutes(sleep_Rem)

        # wake sleep
        sleep_Wake = df2[df2['type'] == 'sleep_Wake']
        awake_sleep = minutes_in_hours_minutes(sleep_Wake)
        streamlit_sleep_stages_chart(duration,deep_sleep,light_sleep, rem_sleep, awake_sleep)        

    elif selected_chart == 'User Engagement':
        # steps
        steps_df = df2[df2['type'] == 'steps']
        steps_df = get_steps_value(steps_df)

        streamlit_steps(steps_df)
        streamlit_steps_pie(steps_df)

        #activity
        totalWearTime_df = df2[df2['type']=='totalWearTime']
        get_user_engagement(totalWearTime_df,sleep_duration)
        get_user_activity(df2)
        get_activity_per_day(df2)