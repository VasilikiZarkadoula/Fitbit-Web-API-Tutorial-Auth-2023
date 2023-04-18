import pandas as pd
import numpy as np
import pymongo
from pymongo import MongoClient
import streamlit as st


# Connect to MongoDB
client = pymongo.MongoClient()
db = client.fitbitDB

# Retrieve data and display in Streamlit
collection = db.demoCollection

# save the documents in a dataframe
df = pd.DataFrame(list(collection.find()))
# drop the _id field, not needed, it is created automatically by MongoDB
df1 = df.drop(['_id'], axis=1)

# setting the screen size
st.set_page_config(layout="wide",page_title="Seattle Airbnb Data")
# main title
st.title('Vasia''s Fitbit Listings MongoDB')
# main text
st.subheader('This app is a Streamlit app that retrieve mongodb data and show it in a dataframe') # subheader
# write text and description
st.write('Data: Sample of Fitbit listing with type, dateTime and value')
# display the dataframe in a table
st.dataframe(df1)
