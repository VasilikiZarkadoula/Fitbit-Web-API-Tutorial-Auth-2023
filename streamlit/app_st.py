import pandas as pd
import pymongo
import streamlit as st
import utils as ut
import plots as pl


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

    pl.streamlit_sleep_layout()

    # sleep duration
    sleep_duration = df2[df2['type'] == 'timeInBed']
    duration = ut.get_minutes_in_hours(sleep_duration)

    # Display the selected chart in an expander
    chart_options = ['Sleep', 'User Engagement']
    selected_chart = st.sidebar.selectbox('Select a chart', chart_options)

    # Display the selected chart
    if selected_chart == 'Sleep':
        # start time
        startTime_df = df2[df2['type'] == 'sleep_startTime']
        startTime_df = ut.get_start_sleep_time(startTime_df)
        pl.streamlit_start_sleep_chart(startTime_df, 'Time (HH:MM)', 'Sleep Start time')
        # timeInBed, minutesAsleep, minutesAwake
        types = ['timeInBed', 'minutesAsleep', 'minutesAwake']
        titles = ['Total Time in bed', 'Total minutes asleep', 'Total minutes awake']
        for idx, x in enumerate(types):
            df = pd.DataFrame()
            df = df2[df2['type'] == x]
            df = ut.get_minutes_in_hour_minutes(df)
            pl.streamlit_sleep_charts(df, 'Time (hh mm)', titles[idx])
            if x == 'timeInBed':
                st.info("This bar chart displays the sleep duration for each day. The y-axis represents the duration of sleep in hours, while the x-axis shows the date. The length of each bar indicates the amount of time spent sleeping for that day. This chart is useful for identifying patterns in sleep duration over time and can help individuals monitor their sleep habits to ensure they are getting enough rest.")
            elif x == 'minutesAsleep':
                st.info("This bar chart shows the total number of hours the user spends asleep each night. It provides a clear visualization of how the user's sleep patterns vary from night to night.")
            elif x == 'minutesAwake':
                st.info("This bar chart shows the total number of hours the user spends awake. It can be useful in identifying patterns of sleep disturbance and how they may be affecting the user's overall sleep quality")
            st.divider()

        # deep sleep
        sleep_Deep = df2[df2['type'] == 'sleep_Deep']
        deep_sleep = ut.get_minutes_in_hours(sleep_Deep)

        # light sleep
        sleep_Light = df2[df2['type'] == 'sleep_Light']
        light_sleep = ut.get_minutes_in_hours(sleep_Light)

        # rem sleep
        sleep_Rem = df2[df2['type'] == 'sleep_Rem']
        rem_sleep = ut.get_minutes_in_hours(sleep_Rem)

        # wake sleep
        sleep_Wake = df2[df2['type'] == 'sleep_Wake']
        awake_sleep = ut.get_minutes_in_hours(sleep_Wake)

        pl.streamlit_sleep_stages_chart(duration, deep_sleep, light_sleep, rem_sleep, awake_sleep)

    elif selected_chart == 'User Engagement':
        # steps
        steps_df = df2[df2['type'] == 'steps']
        steps_df = ut.get_steps_value(steps_df)

        pl.streamlit_steps(steps_df)
        pl.streamlit_steps_pie(steps_df)

        # activity
        totalWearTime_df = df2[df2['type'] == 'totalWearTime']
        pl.streamlit_user_engagement_chart(totalWearTime_df, sleep_duration)
        pl.streamlit_user_activity_chart(df2)
        pl.streamlit_user_activity_per_day_chart(df2)