import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pymongo
import streamlit as st
from datetime import datetime, timedelta, time


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

    # Extract 'minutes' from 'value' column
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


def get_data_value_score(df):
    # Convert 'dateTime' column to datetime objects
    df.loc[:, 'dateTime'] = pd.to_datetime(df['data'].apply(lambda x: x['dateTime']))

    # Set 'dateTime' as the index of the DataFrame
    df.set_index('dateTime', inplace=True)

    # Extract 'score' from 'value' column
    df.loc[:, 'score'] = df['data'].apply(lambda x: x['value'])

    # Drop the 'data' and 'type' columns
    df.drop(['data', 'type'], axis=1, inplace=True)

    # Sort the DataFrame by the 'new_hour' column
    df.sort_values(by='score', inplace=True)
    return df


def streamlit_sleep_layout():
    # setting the screen size
    st.set_page_config(layout="wide", page_title="Fitbit Data")
    # main title
    st.title('Fitbit Sleep MongoDB')
    # main text
    st.subheader('This app is a Streamlit app that retrieve mongodb data and show it in a dataframe')


def streamlit_sleep_charts(df, y_column, y_labels, ylab, title):

    # create a vertical bar chart using Matplotlib
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(df.index, y_column)
    ax.set_xlabel('Date')
    ax.set_ylabel(ylab)
    ax.set_yticklabels(y_labels.values)
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=45)

    # Set x-axis tick labels to show all dates
    plt.xticks(df.index, df.index.strftime('%Y-%m-%d'), rotation=45)

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

# start time
startTime_df = df2[df2['type'] == 'sleep_startTime']
startTime_df = get_start_sleep_time(startTime_df)
y_column = startTime_df['new_hour']
y_labels = startTime_df['hour']
streamlit_sleep_charts(startTime_df, y_column, y_labels, 'Time (HH:MM)', 'Sleep Start time')

# time in bed
timeInBed_df = df2[df2['type'] == 'timeInBed']
timeInBed_df = get_data_value_minutes(timeInBed_df)
y_column = timeInBed_df['hours_minutes']
y_labels = timeInBed_df['hours_minutes']
streamlit_sleep_charts(timeInBed_df,y_column, y_labels, 'Time (hh mm)', 'Total Time in bed')

# minutes Asleep
minutesAsleep_df = df2[df2['type'] == 'minutesAsleep']
minutesAsleep_df = get_data_value_minutes(minutesAsleep_df)
y_column = minutesAsleep_df['hours_minutes']
y_labels = minutesAsleep_df['hours_minutes']
streamlit_sleep_charts(minutesAsleep_df,y_column, y_labels, 'Time (hh mm)', 'Total minutes asleep')


# minutes Awake
minutesAwake_df = df2[df2['type'] == 'minutesAwake']
minutesAwake_df = get_data_value_minutes(minutesAwake_df)
y_column = minutesAwake_df['hours_minutes']
y_labels = minutesAwake_df['hours_minutes']
streamlit_sleep_charts(minutesAwake_df,y_column, y_labels, 'Time (hh mm)', 'Total minutes awake')


# efficiency
efficiency_df = df2[df2['type'] == 'sleep_efficiency']
efficiency_df = get_data_value_score(efficiency_df)
y_column = efficiency_df['score']
y_labels = efficiency_df['score']
streamlit_sleep_charts(efficiency_df, y_column, y_labels, 'Score (/100)', 'Efficiency')

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

# sleep duration
sleep_duration = df2[df2['type'] == 'sleep_duration']
duration = minutes_in_hours_minutes(sleep_duration)

streamlit_sleep_stages_chart(duration,deep_sleep,light_sleep, rem_sleep, awake_sleep)
