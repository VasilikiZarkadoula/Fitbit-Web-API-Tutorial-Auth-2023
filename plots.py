import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from utils import get_data_value, get_activity_value


def streamlit_sleep_layout():
    # setting the screen size
    st.set_page_config(layout="wide", page_title="Fitbit Data")
    # main title
    st.title('Fitbit Sleep MongoDB')
    # main text
    st.subheader('This app is a Streamlit app that retrieve mongodb data and show it in a dataframe')


######################################### sleep charts #########################################


def streamlit_start_sleep_chart(df, y_label, title):
    fig = plt.figure(figsize=(12, 5))

    df = df.sort_values('new_hour')  # sort the DataFrame by new_hour column

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


######################################### user engagement charts #########################################


####### steps charts ########

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


####### activity charts ########


def streamlit_user_engagement_chart(totalWearTime_df, duration_df):

    new_totalWearTime_df = get_data_value(totalWearTime_df)
    new_totalWearTime_df['total_wear_time'] = round(new_totalWearTime_df['value'] / 60, 2)

    new_duration_df = duration_df.applymap(lambda x: x // 60 + (x % 60) / 100)

    merged_df = pd.merge(new_totalWearTime_df, new_duration_df, left_index=True, right_index=True, how='outer')
    merged_df.drop(['value_x'], axis=1, inplace=True)
    merged_df = merged_df.rename(columns={'value_y': 'sleep_duration'})

    # Display plot in Streamlit app
    plt.rcParams['font.size'] = 3

    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    merged_df.plot.bar(x='dateTime', y=['total_wear_time', 'sleep_duration'], ax=ax)
    st.pyplot(fig)


def streamlit_user_activity_chart(df):

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


def streamlit_user_activity_per_day_chart(df):

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
        title='Breakdown of Activity Types by Day'
    ).configure_legend(
        orient='top'
    )

    # Show chart using Streamlit
    st.altair_chart(chart, use_container_width=True)

