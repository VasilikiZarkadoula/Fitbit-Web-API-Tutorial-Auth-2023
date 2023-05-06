import pandas as pd
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
    df['new_hour'] = df.apply(
        lambda row: (datetime.combine(datetime.min, row['hour']) - timedelta(hours=12)).time() if row['hour'] >= time(
            hour=12)
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

    # Make an extra column with the activity level
    df = df.assign(activity_level='normal_activity')

    for index, row in df.iterrows():
        if row['steps'] > 10000:
            df.at[index, 'activity_level'] = 'high_activity'
        elif row['steps'] < 500 and row['steps'] != 0:
            df.at[index, 'activity_level'] = 'low_activity'
        elif row['steps'] == 0:
            df.at[index, 'activity_level'] = 'not_wearing_it'

    return df


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


def get_activity_value(df):

    minutesSedentary_df = get_data_value(df[df['type'] == 'minutesSedentary'])
    minutesLightlyActive_df = get_data_value(df[df['type'] == 'minutesLightlyActive'])
    minutesFairlyActive_df = get_data_value(df[df['type'] == 'minutesFairlyActive'])
    minutesVeryActive_df = get_data_value(df[df['type'] == 'minutesVeryActive'])

    minutesSedentary_df['minutesSedentary'] = round(minutesSedentary_df['value'] / 60, 2)
    minutesLightlyActive_df['minutesLightlyActive'] = round(minutesLightlyActive_df['value'] / 60, 2)
    minutesFairlyActive_df['minutesFairlyActive'] = round(minutesFairlyActive_df['value'] / 60, 2)
    minutesVeryActive_df['minutesVeryActive'] = round(minutesVeryActive_df['value'] / 60, 2)

    minutesSedentary_df.drop(['dateTime', 'value'], axis=1, inplace=True)
    minutesLightlyActive_df.drop(['dateTime', 'value'], axis=1, inplace=True)
    minutesFairlyActive_df.drop(['dateTime', 'value'], axis=1, inplace=True)
    minutesVeryActive_df.drop(['dateTime', 'value'], axis=1, inplace=True)

    return minutesSedentary_df, minutesLightlyActive_df, minutesFairlyActive_df, minutesVeryActive_df



