# Google Calendar Authentication and Access
from __future__ import print_function
from asyncio import subprocess
import datetime
import pytz
import pickle
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
# Speech Engine
import pyttsx3
from decouple import config
import speech_recognition as sr
from random import choice
# These open and execute notepad
import os
import subprocess
# This is another firle
from utils import opening_text
from functions.online_ops import play_on_youtube, search_on_google
from functions.os_ops import open_calculator, open_camera


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

USERNAME = config('USER')
BOTNAME = config('BOTNAME')

# sapi5 - Microsoft API to use voice
engine = pyttsx3.init('sapi5') 

# Set Rate
engine.setProperty('rate', 190)

# Set Volume
engine.setProperty('volume', 1.0)

# Set Voice(Female)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# engine.say("Hello World!")
# engine.say('My current speaking rate is ')
# engine.runAndWait()
# engine.stop()

def speak(text):
    """This will speak anything contained in the text"""
    engine.say(text)
    engine.runAndWait()

# Greet the user
def greet_user():
    hour = datetime.datetime.now().hour
    if (hour >= 6) and (hour < 12):
        speak(f"Good Morning {USERNAME}")
    elif (hour >= 12) and (hour < 16):
        speak(f"Good afternoon {USERNAME}")
    elif (hour >= 16) and (hour < 19):
        speak(f"Good Evening {USERNAME}")
    speak(f"I am {BOTNAME}. How may I assist you?")

def take_user_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening....')
        r.pause_threshold = 1      # won't complain if we pause for 1 sec while we speak
        audio = r.listen(source)

    try:
        print('Recognizing....')
        query = r.recognize_google(audio, language="en-in")
        if not 'exit' in query or 'stop' in query:
            speak(choice(opening_text))
        else:
            speak('Have a good day sir!')
            exit()
    except Exception:
        speak('Sorry, I could not understand. Could you please say that again?')
        query = 'None'
    return query.lower()

def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())         # get's earliest time on day
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())     # get's latest time on day
    utc = pytz.UTC
    date = date.astimezone(utc)            # UTC formatted date
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(), singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    
    else:
        speak(f"You have {len(events)} events on this day")
        # Prints the start and name of the next 10 events
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            start_time = start_time.split(":")
            if int(start_time[0]) < 12:
                start_time = start_time[0] + " " + start_time[1] + "am"
            else:
                start_time = str(int(start_time[0]) - 12) + " " + start_time[1] + "pm" 
            # if int(start_time.split(":")[0]) < 12:
            #     start_time = start_time + "am"
            # else:
            #     start_time = str(int(start_time.split(":")[0]) - 12) + start_time.split(":")[1]
            #     start_time = start_time + "pm"
            speak(event["summary"] + "at" + start_time)
 
def get_date(text):
    # text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0: 
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)   # 5th
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass
    if month < today.month and month != -1:
        year = year + 1
    if day < today.day and month == -1 and day != -1:
        month = month + 1
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            day += 7
            if text.count("next") >= 1:
                dif += 7
        return today + datetime.timedelta(dif)
    
    if month == -1 or day == -1:                # we haven't figured out a day or month                   
        return None
    
    return datetime.date(month=month, day=day, year=year)

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)
    
    subprocess.Popen(["notepad.exe", file_name])

# WAKE = "hey mew"
# SERVICE = authenticate_google()
# print("start")

if __name__ == '__main__':
    # WAKE = "hey mew"
    SERVICE = authenticate_google()
    greet_user()

    while True:
        
        # text = take_user_input()
        # if text.count(WAKE) > 0:
        #     speak("I am ready")

        query = take_user_input()

        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
        for phrase in CALENDAR_STRS:
            if phrase in query:
                date = get_date(query)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("Please try again")

        NOTE_STRS = ["make a note", "write this down", "remember this"]
        for phrase in NOTE_STRS:
            if phrase in query:
                speak("what would you like to me to write down?")
                note_text = take_user_input()
                note(note_text)
                speak("I've made a note of that")


        # query = take_user_input().lower()

        if "open camera" in query:
            open_camera()

        elif "open calculator" in query:
            open_calculator()

        elif 'youtube' in query:
            speak('What do you want to play on Youtube, sir?')
            video = take_user_input().lower()
            play_on_youtube(video)

        elif 'search on google' in query:
            speak('What do you want to search on Google, sir?')
            query = take_user_input().lower()
            search_on_google(query)

            