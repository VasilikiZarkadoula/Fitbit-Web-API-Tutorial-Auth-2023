import pandas as pd
from datetime import datetime, timedelta, time


def get_df_columns(df, datetime_flg, int_flag=True):
    """
    Converts the 'dateTime' column to datetime objects,
    sets 'dateTime' as the index of the DataFrame,
    extracts the value from data - value,
    and drops the 'data' and 'type' columns.
    If datetime_flg is True, adds 'dateTime' column to DataFrame.
    If int_flag is True, converts 'value' column to int.
    """
    df.loc[:, 'dateTime'] = pd.to_datetime(df['data'].apply(lambda x: x['dateTime']))
    df.set_index('dateTime', inplace=True)
    df.loc[:, 'value'] = df['data'].apply(lambda x: x['value'])
    if datetime_flg:
        df.loc[:, 'dateTime'] = df['data'].apply(lambda x: x['dateTime'])
    if int_flag:
        df['value'] = df['value'].astype(int)
    df.drop(['data', 'type'], axis=1, inplace=True)
    return df

def get_start_sleep_time(df):
    """
    Extracts the hour from the "value" key and stores it in a new column,
    converts 'hour' column to datetime objects,
    calculates new_hour based on conditions (if hour > 12:00 then hour -12:00 else if hour < 12:00 then hour + 12:00)
    and converts new_hour to string format.
    Sorts the DataFrame by the 'new_hour' column.
    """
    df = get_df_columns(df, False, False)
    df['hour'] = pd.to_datetime(df.loc[:, 'value']).dt.strftime('%H:%M')
    df['hour'] = pd.to_datetime(df['hour'], format='%H:%M').dt.time
    df['new_hour'] = df.apply(lambda row: (datetime.combine(datetime.min, row['hour']) - timedelta(hours=12)).time()
                               if row['hour'] >= time(hour=12)
                               else (datetime.combine(datetime.min, row['hour']) + timedelta(hours=12)).time(), axis=1)
    df['new_hour'] = df['new_hour'].apply(lambda x: x.strftime('%H:%M'))
    df.sort_values(by='new_hour', inplace=True)
    return df

def get_minutes_in_hour_minutes(df):
    """
    Calculates hours and minutes and combines them in a new column,
    drops the 'hours' and 'minutes' columns,
    and sorts the DataFrame by the 'hours_minutes' column.
    """
    df = get_df_columns(df, False)
    df['hours'] = df['value'] // 60
    df['minutes'] = df['value'] % 60
    df['hours'] = df['hours'].apply(lambda x: '{:02d}h'.format(x))
    df['minutes'] = df['minutes'].apply(lambda x: '{:02d}m'.format(x))
    df['hours_minutes'] = df['hours'] + ' ' + df['minutes']
    df.drop(['hours', 'minutes'], axis=1, inplace=True)
    df.sort_values(by='hours_minutes', inplace=True)
    return df

def get_minutes_in_hours(df):
    """
    Converts minutes to hours and minutes format.
    """
    df = get_df_columns(df, False)
    new_df = df.applymap(lambda x: x // 60 + (x % 60) / 100)
    return new_df['value']


def get_steps_value(df):
    """
    Calculates activity level based on the 'value' column in the input DataFrame.
    """
    df = get_df_columns(df, False)

    # Sort the DataFrame by the 'dateTime' column
    df = df.sort_values(by='dateTime')

    # Make an extra column with the activity level
    df = df.assign(activity_level='normal_activity')

    for index, row in df.iterrows():
        if row['value'] > 10000:
            df.at[index, 'activity_level'] = 'high_activity'
        elif row['value'] < 500 and row['value'] != 0:
            df.at[index, 'activity_level'] = 'low_activity'
        elif row['value'] == 0:
            df.at[index, 'activity_level'] = 'not_wearing_it'

    return df


def get_activity_value(df):
    """
    Extracts the minutes of sedentary, light, fairly and very active from the input DataFrame,
    and rounds to 2 decimal places.
    """
    minutesSedentary_df = get_df_columns(df[df['type'] == 'minutesSedentary'], True)
    minutesLightlyActive_df = get_df_columns(df[df['type'] == 'minutesLightlyActive'], True)
    minutesFairlyActive_df = get_df_columns(df[df['type'] == 'minutesFairlyActive'], True)
    minutesVeryActive_df = get_df_columns(df[df['type'] == 'minutesVeryActive'], True)

    minutesSedentary_df['minutesSedentary'] = round(minutesSedentary_df['value'] / 60, 2)
    minutesLightlyActive_df['minutesLightlyActive'] = round(minutesLightlyActive_df['value'] / 60, 2)
    minutesFairlyActive_df['minutesFairlyActive'] = round(minutesFairlyActive_df['value'] / 60, 2)
    minutesVeryActive_df['minutesVeryActive'] = round(minutesVeryActive_df['value'] / 60, 2)

    minutesSedentary_df.drop(['dateTime', 'value'], axis=1, inplace=True)
    minutesLightlyActive_df.drop(['dateTime', 'value'], axis=1, inplace=True)
    minutesFairlyActive_df.drop(['dateTime', 'value'], axis=1, inplace=True)
    minutesVeryActive_df.drop(['dateTime', 'value'], axis=1, inplace=True)

    return minutesSedentary_df, minutesLightlyActive_df, minutesFairlyActive_df, minutesVeryActive_df



