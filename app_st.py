import pandas as pd
import pymongo
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time


def get_start_sleep_time(df):

    # Convert 'dateTime' column to datetime objects
    df.loc[:, 'dateTime'] = pd.to_datetime(df['data'].apply(lambda x: x['dateTime']))

    # Set 'dateTime' as the index of the DataFrame
    df.set_index('dateTime', inplace=True)

    # Extract 'hour' from 'value' column
    df.loc[:, 'hour'] = df['data'].apply(lambda x: x['value'])

    # Drop the 'data' and 'type' columns
    df.drop(['data', 'type'], axis=1, inplace=True)

    # Extract hour from 'hour' column and convert to datetime objects
    df['hour'] = pd.to_datetime(df['hour'], format='%H:%M')
    df['hour'] = df['hour'].dt.strftime('%H:%M')


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

    # Extract 'hour' from 'value' column
    df.loc[:, 'minutes'] = df['data'].apply(lambda x: x['value'])

    # Drop the 'data' and 'type' columns
    df.drop(['data', 'type'], axis=1, inplace=True)

    df['minutes'] = df['minutes'].astype(int)
    # Calculate hours and minutes
    df['hours'] = df['minutes'] // 60
    df['minutes'] = df['minutes'] % 60
    df['hours'] = df['hours'].apply(lambda x: '{:02d}h'.format(x))
    df['minutes'] = df['minutes'].apply(lambda x: '{:02d}m'.format(x))
    df['hours_minutes'] = df['hours'] + ' ' + df['minutes']

    # Sort the DataFrame by the 'new_hour' column
    df.sort_values(by='hours_minutes', inplace=True)
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


# Connect to MongoDB
client = pymongo.MongoClient()
db = client.fitbitDB
collection = db.demoCollection

# save the documents in a dataframe
df = pd.DataFrame(list(collection.find()))
# drop the _id and id fields, not needed
df1 = df.drop(['_id'], axis=1)
df2 = df1.drop(['id'], axis=1)


# sleep
streamlit_sleep_layout()

# start time
startTime_df = df2[df2['type'] == 'startTime']
startTime_df = get_start_sleep_time(startTime_df)
y_column = startTime_df['new_hour']
y_labels = startTime_df['hour']
streamlit_sleep_charts(startTime_df,y_column, y_labels,'Time (HH:MM)', 'Sleep Start time')

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
