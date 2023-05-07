import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from utils import get_df_columns, get_activity_value


def streamlit_sleep_layout():
    """
    Set the screen size and create the layout for the sleep dashboard in Streamlit.
    """
    st.set_page_config(layout="wide", page_title="Fitbit Data")
    st.title('Fitbit Sleep MongoDB')
    st.subheader('This app is a Streamlit app that retrieve mongodb data and show it in a dataframe')

######################################### sleep charts #########################################


def streamlit_start_sleep_chart(df, y_label, title):
    """
    Plot a bar chart for the sleep start time from given DataFrame.
    """
    df = df.sort_values('new_hour')  # sort the DataFrame by new_hour column
    plt.rcParams['font.size'] = 4
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    #fig = plt.figure(figsize=(12, 5))
    plt.bar(df.index, df['new_hour'])
    plt.xlabel('Date')
    plt.xticks(df.index, df.index.strftime('%Y-%m-%d'), rotation=90, ha='center')
    plt.ylabel(y_label)
    plt.yticks(df['new_hour'], df['hour'])
    plt.title(title)

    plt.tight_layout()
    st.pyplot(fig)
    st.write("")
    st.divider()

def streamlit_sleep_charts(df, y_label, title):
    """
    Plot a bar chart for the sleep duration from given DataFrame.
    """
    plt.rcParams['font.size'] = 4
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    ax.bar(df.index, df['hours_minutes'])
    ax.set_xlabel('Date')
    plt.xticks(df.index, df.index.strftime('%Y-%m-%d'), rotation=90)
    ax.set_ylabel(y_label)
    ax.set_yticklabels(df['hours_minutes'].values)
    ax.set_title(title)

    plt.tight_layout()
    st.pyplot(fig)
    st.write("")
    st.divider()


def streamlit_sleep_stages_chart(duration, deep_sleep, light_sleep, rem_sleep, awake_sleep):
    """
    Plot a bar chart for the different stages of sleep from given DataFrame.
    """
    st.subheader("# This is a heading")
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
    plt.rcParams['font.size'] = 4
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    ax.bar(r1, duration, width=bar_width, label='Sleep duration')
    ax.bar(r2, light_sleep, width=bar_width, label='Light Sleep')
    ax.bar(r3, deep_sleep, width=bar_width, label='Deep Sleep')
    ax.bar(r4, rem_sleep, width=bar_width, label='REM Sleep')
    ax.bar(r5, awake_sleep, width=bar_width, label='Wake Sleep')

    ax.set_xticks(r2)
    ax.set_xticklabels(dates, rotation=90)
    ax.set_xlabel('Date')
    ax.set_ylabel('Hours')
    ax.set_title('Sleep Data')
    ax.legend()

    plt.tight_layout()
    st.pyplot(fig)
    st.write("")
    st.divider()

######################################### user engagement charts #########################################

####### steps charts ########

def streamlit_steps(df):
    """
    Plots a scatter plot with the steps taken per day, along with a line plot
    that connects the dots and horizontal lines at 10000 and 500 steps.
    """
    plt.rcParams['font.size'] = 4
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    ax.scatter(df.index, df['value'], color='b')

    for dateTime, row in df.iterrows():
        ax.text(dateTime, row['value'], str(int(row['value'])), ha='center', va='bottom', fontdict={'size': 9})

    ax.axhline(y=10000, color='green', linestyle='--', alpha=0.5)
    ax.axhline(y=500, color='magenta', linestyle='--', alpha=0.5)

    # Create a line plot with the same x-axis values and the 'steps' column of the DataFrame
    ax.plot(df.index, df['value'], color='r')

    tick_labels = df.index.strftime('%Y-%m-%d')
    ax.set_xticks(df.index)
    ax.set_xlabel('Date')
    ax.set_xticklabels(tick_labels, rotation=90)
    ax.set_yticks(
        np.arange(df['value'].min(), df['value'].max() + 10000, 1000))  # Set y-axis ticks to a range of values
    ax.set_ylim(df['value'].min(), df['value'].max() + 1500)  # Set y-axis limits to a range of values
    ax.set_ylabel('Steps')
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
    ax.set_title('Steps per Day')

    plt.tight_layout()
    st.pyplot(fig)
    st.write("")
    st.divider()


def streamlit_steps_pie(df):
    """
    Creates a pie chart that displays the percentage of activity level based
    on the number of steps.
    """
    # count the number of occurrences of each value in the activity_level column
    value_counts = df['activity_level'].value_counts(normalize=True)

    plt.rcParams['font.size'] = 4
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    ax.pie(
        value_counts.values,
        labels=value_counts.index,
        autopct='%1.1f%%',
        colors=['purple', 'green', 'blue', 'gray'],
        startangle=90
    )
    ax.set_title('Percentage of activity level based on the number of steps')
    ax.set_box_aspect(0.4)  # adjust the aspect ratio of the plot to make it less zoomed in
    fig.set_dpi(200)  # adjust the resolution of the plot

    plt.tight_layout()
    st.pyplot(fig)
    st.write("")
    st.divider()


####### activity charts ########

def streamlit_user_engagement_chart(totalWearTime_df, duration_df):
    """
    Generates a bar chart showing the user's total wear time and sleep duration per day.
    """
    new_totalWearTime_df = get_df_columns(totalWearTime_df, True)
    new_totalWearTime_df['total_wear_time'] = round(new_totalWearTime_df['value'] / 60, 2)

    new_duration_df = duration_df.apply(pd.to_numeric)
    new_duration_df = new_duration_df.applymap(lambda x: x // 60 + (x % 60) / 100)

    merged_df = pd.merge(new_totalWearTime_df, new_duration_df, left_index=True, right_index=True, how='outer')
    merged_df.drop(['value_x'], axis=1, inplace=True)
    merged_df = merged_df.rename(columns={'value_y': 'sleep_duration'})

    plt.rcParams['font.size'] = 4
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    merged_df.plot.bar(x='dateTime', y=['total_wear_time', 'sleep_duration'], ax=ax)
    ax.set_title('Total wear time vs sleep duration')
    ax.set_ylabel('Hours')
    st.pyplot(fig)
    st.write("A bar chart showing the total wear time and sleep duration per day provides a quick glance at how much time the user spends wearing their activity tracker and how much time they spend sleeping. By comparing the two bars for each day, the user can quickly see if they are getting enough sleep and if they are consistently wearing their tracker throughout the day. This information can be useful in identifying patterns and making changes to improve overall health and wellness.")
    st.divider()


def streamlit_user_activity_chart(df):
    """
    Generates a pie chart showing the percentage of time spent in each activity level.
    """
    minutesSedentary_df, minutesLightlyActive_df, minutesFairlyActive_df, minutesVeryActive_df = get_activity_value(df)

    sedentary_time = minutesSedentary_df.sum()['minutesSedentary']
    lightly_active_time = minutesLightlyActive_df.sum()['minutesLightlyActive']
    fairly_active_time = minutesFairlyActive_df.sum()['minutesFairlyActive']
    very_active_time = minutesVeryActive_df.sum()['minutesVeryActive']

    # Create pie chart
    labels = ['Very', 'Sedentary', 'Fairly', 'Lightly']
    sizes = [very_active_time, sedentary_time, fairly_active_time, lightly_active_time]
    plt.rcParams['font.size'] = 4

    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    ax.set_title('Percentage of Time Spent in Each Activity Level')
    st.pyplot(fig)
    st.write("This pie chart shows the percentage of time spent in each activity level, including minutes spent sedentary, lightly active, fairly active, and very active. The chart provides an easy-to-understand visualization of how time is allocated across different activity levels, and can help users identify areas where they may want to increase their activity levels.")
    st.divider()


def streamlit_user_activity_per_day_chart(df):
    """
    Generates a stacked bar chart showing the breakdown of activity types by day.
    """
    minutesSedentary_df, minutesLightlyActive_df, minutesFairlyActive_df, minutesVeryActive_df = get_activity_value(df)

    merged_df = pd.merge(minutesSedentary_df, minutesLightlyActive_df, left_index=True, right_index=True, how='outer')
    # merged_df.drop(['value_x','dateTime_x','value_y'], axis=1, inplace=True)

    merged_df1 = pd.merge(merged_df, minutesFairlyActive_df, left_index=True, right_index=True, how='outer')
    # merged_df1.drop(['dateTime_y','value'], axis=1, inplace=True)

    merged_df2 = pd.merge(merged_df1, minutesVeryActive_df, left_index=True, right_index=True, how='outer')
    # merged_df2.drop(['dateTime_x','value'], axis=1, inplace=True)
    merged_df2 = merged_df2.rename(columns={'dateTime_y': 'dateTime'})

    # Create stacked bar chart
    plt.rcParams['font.size'] = 4
    merged_df2 = merged_df2.reset_index()

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
        title={
        "text": "Breakdown of Activity Types by Day",
        "align": "center",
        "fontSize": 18
        }
    ).configure_legend(
        orient='top'
    ).configure(background='#FFFFFF')

    # Show chart using Streamlit
    st.altair_chart(chart, use_container_width=True)
    st.write("This stacked bar chart shows the breakdown of each activity type (minutesSedentary, minutesLightlyActive, minutesFairlyActive, minutesVeryActive) by day. The chart provides insight into the user's daily activity levels and can help identify trends over time")
    st.divider()
