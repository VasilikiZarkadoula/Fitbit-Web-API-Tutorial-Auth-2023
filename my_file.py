import pymongo
import streamlit as st

client = pymongo.MongoClient()
db = client.fitbitDB
collection = db.demoCollection
data = collection.find()  # You can specify query conditions within the find() method

# Loop through the retrieved data and display it in Streamlit
for document in data:
    # Access document fields and display the data in Streamlit components
    # (e.g., st.write(), st.table(), etc.)
    st.write(document)