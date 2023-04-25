import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd 
import datetime
import matplotlib.pyplot as plt
import hashlib
import random
from pymongo import MongoClient
import requests


def df_fitbit(activity, base_date, end_date, token):
    url = 'https://api.fitbit.com/1.2/user/-/' + activity + '/date/' + base_date + '/' + end_date + '.json'
    response = requests.get(url=url, headers={'Authorization':'Bearer ' + token}).json()

    return response

def create_data(dicts,types):
    data_list = []
    # loop through each nested dictionary
    for i in range(0,len(dicts)):        
        # create a random hash ID
        hash_object = hashlib.sha256(str(random.getrandbits(256)).encode())
        id = hash_object.hexdigest()           
        # create a new dictionary with the id, type, and data fields
        new_dict = {
            'id': id,
            'type': types,
            'data': dicts[i]
        }           
        # append the new dictionary to the output list
        data_list.append(new_dict)
    return data_list  

if __name__ == "__main__":
    # vassia.zrk@gmail.com
    # FitBitLab2023
    # YOU NEED TO PUT IN YOUR OWN CLIENT_ID AND CLIENT_SECRET
    CLIENT_ID='23QQNX'
    CLIENT_SECRET='2cf8156ff7b81eadd26d80a30082067c'

    server=Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()
    ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])
    auth2_client=fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)

    token = ACCESS_TOKEN
    base_date = '2023-03-29'
    end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    #data to gather
    sleepList = df_fitbit('sleep', base_date, end_date, token)['sleep']
    sleepDictList = []
    for sleepItem in sleepList:
        mainSleep = sleepItem['isMainSleep']
        if mainSleep == True:
            sleepDict = {
                "dateOfSleep": sleepItem['dateOfSleep'], 
                "startTime": sleepItem['startTime'], 
                "endTime": sleepItem['endTime'], 
                "efficiency": sleepItem['efficiency'],
                "minutesAfterWakeup": sleepItem['minutesAfterWakeup'],
                "minutesAsleep": sleepItem['minutesAsleep'],
                "minutesAwake": sleepItem['minutesAwake'],
                "timeInBed": sleepItem['timeInBed'],
                "summary": sleepItem['levels']['summary']
                }
            sleepDictList.append(sleepDict)

    activityList = ['activities/minutesSedentary', 'activities/minutesLightlyActive','activities/minutesFairlyActive','activities/minutesVeryActive', 'activities/steps', 'activities/heart']
    minutesSedentary = df_fitbit(activityList[0], base_date, end_date, token)['activities-minutesSedentary']

    minutesLightlyActive = df_fitbit(activityList[1], base_date, end_date, token)['activities-minutesLightlyActive']

    minutesFairlyActive = df_fitbit(activityList[2], base_date, end_date, token)['activities-minutesFairlyActive']

    minutesVeryActive = df_fitbit(activityList[3], base_date, end_date, token)['activities-minutesVeryActive']

    heartRate = df_fitbit(activityList[5], base_date, end_date, token)['activities-heart']

    activityDictList = []

    for sedentary in minutesSedentary:
        datetimeSed = sedentary['dateTime']
        totalTime = int(sedentary['value'])

        for heart in heartRate:
            if heart['dateTime'] == datetimeSed:
                if totalTime == 1440:
                    totalTime = 0
                for lightlyActive in minutesLightlyActive:
                    if datetimeSed == lightlyActive['dateTime']:
                        totalTime += int(lightlyActive['value'])
                
                for fairlyActive in minutesFairlyActive:
                    if datetimeSed == fairlyActive['dateTime']:
                        totalTime += int(fairlyActive['value'])

                for veryActive in minutesVeryActive:
                    if datetimeSed == veryActive['dateTime']:
                        totalTime += int(veryActive['value'])

        activityDict = {
            "datetimeSed": datetimeSed, 
            "totalWearTime": totalTime, 
            }
        activityDictList.append(activityDict)
    
    
    activity_data = create_data(activityDictList,"activity")
    print(activity_data)

    heart_data = create_data(heartRate,"heartRate")
    print(heart_data)

    sleep_data = create_data(sleepDictList,"sleep")
    print(sleep_data)

    # establing connection
    try:
        connect = MongoClient()
        print("Connected successfully!!!")
    except:
        print("Could not connect to MongoDB")

    # connecting or switching to the database
    db = connect.fitbitDB

    # creating or switching to demoCollection
    collection = db.demoCollection

    # Inserting activity documents one by one
    for document in activity_data:
        collection.insert_one(document)
    
    for document in heart_data:
        collection.insert_one(document)

    for document in sleep_data:
        collection.insert_one(document)