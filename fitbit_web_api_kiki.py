import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd 
import datetime
import matplotlib.pyplot as plt
import hashlib
import random
from pymongo import MongoClient
import requests
from datetime import timedelta


def df_fitbit(activity, base_date, end_date, token):
    url = 'https://api.fitbit.com/1.2/user/-/' + activity + '/date/' + base_date + '/' + end_date + '.json'
    response = requests.get(url=url, headers={'Authorization':'Bearer ' + token}).json()

    return response

def create_data(dictItem,typeItem):
    data_list = []
    # create a random hash ID
    hash_object = hashlib.sha256(str(random.getrandbits(256)).encode())
    id = hash_object.hexdigest()  
    # create a new dictionary with the id, type, and data fields
    new_dict = {
        'id': id,
        'type': typeItem,
        'data': dictItem
      }           
        # append the new dictionary to the output list
    collection.insert_one(new_dict)
    return data_list  

def getSleepData():
    #data to gather
    sleepList = df_fitbit('sleep', base_date, end_date, token)['sleep']
    sleepDictList = []
    milliseconds = 3600000  # Example value

    # Create a timedelta object with the milliseconds as the total number of microseconds
    for sleepItem in sleepList:
        mainSleep = sleepItem['isMainSleep']
        if mainSleep == True:
            duration = int(sleepItem['duration']) / 3600000
            durationDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "duration": round(duration,2)
            }
            create_data(durationDict,"duration")

            startTimeDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "startTime": sleepItem['startTime']
            }
            create_data(startTimeDict,"startTime")

            endTimeDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "endTime": sleepItem['endTime']
            }
            create_data(endTimeDict,"endTime")

            timeInBedDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "timeInBed": sleepItem['timeInBed']
            }
            create_data(timeInBedDict,"timeInBed")

            minutesAsleepDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "minutesAsleep": sleepItem['minutesAsleep']
            }
            create_data(minutesAsleepDict,"minutesAsleep")

            minutesAwakeDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "minutesAwake": sleepItem['minutesAwake']
            }
            create_data(minutesAwakeDict,"minutesAwake")

            efficiencyDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "efficiency": sleepItem['efficiency']
            }
            create_data(efficiencyDict,"efficiency")

            summaryDeepDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "minutes": sleepItem['levels']['summary']['deep']['minutes']
            }
            create_data(summaryDeepDict,"summaryDeep")

            summaryLightDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "minutes": sleepItem['levels']['summary']['light']['minutes']
            }
            create_data(summaryLightDict,"summaryLight")

            summaryRemDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "minutes": sleepItem['levels']['summary']['rem']['minutes']
            }
            create_data(summaryRemDict,"summaryRem")

            summaryWakeDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "minutes": sleepItem['levels']['summary']['wake']['minutes']
            }
            create_data(summaryWakeDict,"summaryWake")
        
        
def getActivityData():

    activityList = ['activities/minutesSedentary', 'activities/minutesLightlyActive','activities/minutesFairlyActive','activities/minutesVeryActive', 'activities/steps', 'activities/heart']
    minutesSedentary = df_fitbit(activityList[0], base_date, end_date, token)['activities-minutesSedentary']

    minutesLightlyActive = df_fitbit(activityList[1], base_date, end_date, token)['activities-minutesLightlyActive']

    minutesFairlyActive = df_fitbit(activityList[2], base_date, end_date, token)['activities-minutesFairlyActive']

    minutesVeryActive = df_fitbit(activityList[3], base_date, end_date, token)['activities-minutesVeryActive']

    heartRate = df_fitbit(activityList[5], base_date, end_date, token)['activities-heart']
    for sedentary in minutesSedentary:
        datetimeSed = sedentary['dateTime']
        totalTime = int(sedentary['value'])
        
        for heart in heartRate:
            if heart['dateTime'] == datetimeSed:
                if totalTime == 1440:
                    totalTime = 0
                minutesSedentary = {
                    "dateTime": datetimeSed, 
                    "minutesSedentary": totalTime, 
                    } 
                create_data(minutesSedentary,"minutesSedentary")

                for lightlyActive in minutesLightlyActive:
                    if not isinstance(lightlyActive, str) and datetimeSed == lightlyActive['dateTime']:
                        minutesLightlyActive = {
                            "dateTime": datetimeSed, 
                            "minutesLightlyActive": int(lightlyActive['value']), 
                            } 
                        create_data(minutesLightlyActive,"minutesLightlyActive")

                        totalTime += int(lightlyActive['value'])
                
                for fairlyActive in minutesFairlyActive:
                    if not isinstance(fairlyActive, str) and datetimeSed == fairlyActive['dateTime']:
                        minutesFairlyActive = {
                            "dateTime": datetimeSed, 
                            "minutesFairlyActive": int(fairlyActive['value']), 
                            } 
                        create_data(minutesFairlyActive,"minutesFairlyActive")

                        totalTime += int(fairlyActive['value'])

                for veryActive in minutesVeryActive:
                    if not isinstance(veryActive, str) and datetimeSed == veryActive['dateTime']:
                        minutesVeryActive = {
                            "dateTime": datetimeSed, 
                            "minutesVeryActive": int(veryActive['value']), 
                            } 
                        create_data(minutesVeryActive,"minutesVeryActive")
                    
                        totalTime += int(veryActive['value'])

        activityDict = {
            "dateTime": datetimeSed, 
            "totalWearTime": totalTime, 
            }    
    
        create_data(activityDict,"totalWearTime")

def getStepsData():
    steps_count = df_fitbit('activities/steps', base_date, end_date, token)['activities-steps']

    highly_active_days = []
    for i in range(0, len(steps_count)):
        steps = steps_count[i].get('value')
        stepsDict = {
            "dateTime": steps_count[i].get('dateTime'), 
            "steps": steps, 
            }    
        create_data(stepsDict,"steps")

        if int(steps) >= 10000:
            highly_active_days = {
                "dateTime": steps_count[i].get('dateTime'), 
                "steps": steps, 
                }    
            create_data(stepsDict,"highly_active_days")

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

    getSleepData()

    getActivityData()

    getStepsData()